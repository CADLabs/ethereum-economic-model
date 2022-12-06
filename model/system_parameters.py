"""
Definition of System Parameters, their types, and default values.

By using a dataclass to represent the System Parameters:
* We can use types for Python type hints
* Set default values
* Ensure that all System Parameters are initialized
"""


import logging
import numpy as np
from dataclasses import dataclass
from datetime import datetime

import model.constants as constants
import experiments.simulation_configuration as simulation
from model.types import (
    Run,
    Timestep,
    Percentage,
    Gwei,
    Gas,
    Gwei_per_Gas,
    ETH,
    POLYGN,
    USD_per_epoch,
    Percentage_per_epoch,
    ValidatorEnvironment,
    List,
    Callable,
    Epoch,
    Stage,
)
from model.utils import default
from data.historical_values import (
    eth_price_mean,
    eth_block_rewards_mean,
)
from data.api import subgraph


mean_validator_deposits_per_epoch = (
    ## TODO: Need to change another subgraph api
    subgraph.get_6_month_mean_validator_deposits_per_epoch(default=3) 
)

# Configure validator environment distribution
validator_environments = [
    # Configure a custom validator environment using the following as a template:
    # ValidatorEnvironment(
    #     type="custom",
    #     percentage_distribution=0.01,  # 1%
    #     hardware_costs_per_epoch=0.0014,
    #     cloud_costs_per_epoch=0,
    #     third_party_costs_per_epoch=0,
    # ),
    ValidatorEnvironment(
        type="diy_hardware",
        percentage_distribution=0.37,
        hardware_costs_per_epoch=0.0014,
    ),
    ValidatorEnvironment(
        type="diy_cloud",
        percentage_distribution=0.13,
        cloud_costs_per_epoch=0.00027,
    ),
    ValidatorEnvironment(
        type="pool_staas",
        percentage_distribution=0.27,
        third_party_costs_per_epoch=0.12,
    ),
    ValidatorEnvironment(
        type="pool_hardware",
        percentage_distribution=0.05,
        hardware_costs_per_epoch=0.0007,
    ),
    ValidatorEnvironment(
        type="pool_cloud",
        percentage_distribution=0.02,
        cloud_costs_per_epoch=0.00136,
    ),
    ValidatorEnvironment(
        type="staas_full",
        percentage_distribution=0.08,
        third_party_costs_per_epoch=0.15,
    ),
    ValidatorEnvironment(
        type="staas_self_custodied",
        percentage_distribution=0.08,
        third_party_costs_per_epoch=0.12,
    ),
]
"""Validator environment configuration

See ASSUMPTIONS.md document for details of validator environment configuration and assumptions.
"""

# Normalise percentage distribution to a total of 100%
total_percentage_distribution = sum(
    [validator.percentage_distribution for validator in validator_environments]
)

if total_percentage_distribution < 1:
    logging.warning(
        """
        Parameter validator.percentage_distribution normalized due to sum not being equal to 100%
        """
    )
    for validator in validator_environments:
        validator.percentage_distribution /= total_percentage_distribution

# Using list comprehension, map the validator types to each parameter
validator_percentage_distribution = [
    np.array(
        [validator.percentage_distribution for validator in validator_environments],
        dtype=Percentage,
    )
]
validator_hardware_costs_per_epoch = [
    np.array(
        [validator.hardware_costs_per_epoch for validator in validator_environments],
        dtype=USD_per_epoch,
    )
]
validator_cloud_costs_per_epoch = [
    np.array(
        [validator.cloud_costs_per_epoch for validator in validator_environments],
        dtype=USD_per_epoch,
    )
]
validator_third_party_costs_per_epoch = [
    np.array(
        [validator.third_party_costs_per_epoch for validator in validator_environments],
        dtype=Percentage_per_epoch,
    )
]


@dataclass
class Parameters:
    """System Parameters
    Each System Parameter is defined as:
    system parameter key: system parameter type = default system parameter value

    Because lists are mutable, we need to wrap each parameter list in the `default(...)` method.

    For default value assumptions, see the ASSUMPTIONS.md document.
    """

    # Time parameters
    dt: List[Epoch] = default([simulation.DELTA_TIME])
    """
    Simulation timescale / timestep unit of time, in epochs.

    Used to scale calculations that depend on the number of epochs that have passed.

    For example, for dt = 100, each timestep equals 100 epochs.

    By default set to constants.epochs_per_day (~= 225)
    """

    date_start: List[datetime] = default([datetime.now()])
    """Start date for simulation as Python datetime"""



    # Environmental processes
    polygn_price_process: List[Callable[[Run, Timestep], POLYGN]] = default(
        [lambda _run, _timestep: 1.0]
    )
    """
    A process that returns the ETH spot price at each epoch.
    
    By default set to average ETH price over the last 12 months from Etherscan.
    """

    polygn_staked_process: List[Callable[[Run, Timestep], POLYGN]] = default(
        [lambda _run, _timestep: None]
    )
    """
    A process that returns the ETH staked at each epoch.

    If set to `none`, the model is driven by the validator process,
    where new validators enter the system and stake accordingly.

    This process is used for simulating a series of ETH staked values directly.
    """

    validator_process: List[Callable[[Run, Timestep], int]] = default(
        [
            lambda _run, _timestep: mean_validator_deposits_per_epoch,
        ]
    )
    """
    A process that returns the number of new validators added to the activation queue per epoch.

    Used if model not driven using `eth_staked_process`.

    The value comes from The Graph Subgraph
    https://thegraph.com/explorer/subgraph?id=0x540b14e4bd871cfe59e48d19254328b5ff11d820-0
    using the mean value over the last 6 months from the time the model is executed.

    The default value set to 3 comes from https://beaconscan.com/stat/validator
    using the mean value over the last 6 months from February 26 2021 to August 26 2021.
    """

    # Ethereum system parameters
    daily_pow_issuance: List[ETH] = default([eth_block_rewards_mean])
    """
    The average daily Proof-of-Work issuance in ETH.

    See https://etherscan.io/chart/blockreward
    """

    MIN_PER_EPOCH_CHURN_LIMIT: List[int] = default([4])
    """
    Used to calculate the churn limit for validator entry and exit. The maximum number of validators that can
    enter or exit the system per epoch.
    In this system it is used for the validator activation queue process.
    """
    ## TODO: the number is arbitrary, need to find a source for this
    MIN_SLASHING_PENALTY_QUOTIENT: List[int] = default([1e7])
    """
    Used to calculate the penalty applied for a slashable offence.
    """
    MAX_VALIDATOR_COUNT: List[int] = default([100])
    """
    A proposal to set the maximum validators (2**19 == 524,288 validators)
    that are validating ("awake") at any given time. This proposal does not stop validators from 
    depositing and becoming active validators, but rather introduces a rotating validator set.
    "Awake" validators are a subset of "active" validators.

    To disable the maximum validator cap, MAX_VALIDATOR_COUNT is set to None.

    The economic impact of this is as follows:
    
    > Once the active validator set size exceeds MAX_VALIDATOR_COUNT,
    > validator returns should start decreasing proportionately to 1/total_deposits
    > and not 1/sqrt(total_deposits).
    
    See https://ethresear.ch/t/simplified-active-validator-cap-and-rotation-proposal
    
    > The goal of this proposal is to cap the active validator set to some fixed value...
    """
    ELASTICITY_MULTIPLIER: List[int] = default([2])
    """
    Used to calculate gas limit from EIP-1559 gas target
    """
    MAX_EFFECTIVE_BALANCE: Gwei = default([10_000_000_000 * 10 ** 9])
    EFFECTIVE_BALANCE_INCREMENT: Gwei = default([1_000_000 * 10 ** 9])

    # PoS Inflation Parameters:
    inflationary_rate_per_year: List[Percentage] = default([0.01 * constants.gwei])
    """
    The annual rate of inflation for the PoS system.
    """

    # Treasury parameters
    BASE_FEE_PUBLIC_QUOTIENT: List[float] = default([1])
    """
    The parameter of quotient of transaction fees from public chains committed to Polygon Treasury
    """
    BASE_FEE_PRIVATE_QUOTIENTT: List[float] = default([0.1])
    """
    The parameter of quotient of transaction fees from public chains committed to Polygon Treasury
    """
    domain_treasury_monthly_unlock_process: List[Callable[[Run, Timestep], float]] = default(
        [lambda _run, _timestep: 0.01]  # Gwei per gas
    )
    """
    A process that returns the monthly unlock percentage of the total treasury balance.
    """

    # Validator parameters
    validator_uptime_process: List[Percentage] = default(
        [lambda _run, _timestep: max(0.98, 2 / 3)]
    )
    """
    The combination of validator internet, power, and technical uptime, as a percentage.

    Minimum uptime is inactivity leak threshold = 2/3, as this model doesn't model the inactivity leak process.
    """
    validator_percentage_distribution: List[np.ndarray] = default(
        validator_percentage_distribution
    )
    """
    The percentage of validators in each environment, normalized to a total of 100%.

    A vector with a value for each validator environment.
    """
    validator_hardware_costs_per_epoch: List[np.ndarray] = default(
        validator_hardware_costs_per_epoch
    )
    """
    The validator hardware costs per epoch in dollars.

    A vector with a value for each validator environment.
    """
    validator_cloud_costs_per_epoch: List[np.ndarray] = default(
        validator_cloud_costs_per_epoch
    )
    """
    The validator cloud costs per epoch in dollars.

    A vector with a value for each validator environment.
    """
    validator_third_party_costs_per_epoch: List[np.ndarray] = default(
        validator_third_party_costs_per_epoch
    )
    """
    The validator third-party costs as a percentage of total online validator rewards.

    Used for expected Staking-as-a-Service fees.

    A vector with a value for each validator environment.
    """

    # Rewards, penalties, and slashing
    slashing_events_per_1000_epochs: List[int] = default([1])  # 1 / 1000 epochs
    """
    The number of slashing events per 1000 epochs.
    """

    # EIP-1559 transaction pricing parameters
    base_fee_process: List[Callable[[Run, Timestep], Gwei_per_Gas]] = default(
        [lambda _run, _timestep: 30]  # Gwei per gas
    )
    """
    EIP-1559 transaction pricing base fee burned, in Gwei per gas, for each transaction.
    See https://eips.ethereum.org/EIPS/eip-1559 for EIP-1559 proposal.

    See ASSUMPTIONS.md doc for further details about default value assumption.

    An extract from https://notes.ethereum.org/@vbuterin/eip-1559-faq:
    
    > Each “full block” (ie. a block whose gas is 2x the TARGET) increases the BASEFEE by 1.125x,
    > so a series of constant full blocks will increase the gas price by a factor of 10 every
    > ~20 blocks (~4.3 min on average).
    > Hence, periods of heavy on-chain load will not realistically last longer than ~5 minutes.
    """

    priority_fee_process: List[Callable[[Run, Timestep], Gwei_per_Gas]] = default(
        [lambda _run, _timestep: 2]  # Gwei per gas
    )
    """
    EIP-1559 transaction pricing average priority fee, in Gwei per gas, for each transaction.
    See https://eips.ethereum.org/EIPS/eip-1559 for EIP-1559 proposal.
    
    See ASSUMPTIONS.md doc for further details about default value assumption.
    """

    gas_target_process: List[Callable[[Run, Timestep], Gas]] = default(
        [lambda _run, _timestep: 15e6]  # Gas per block
    )
    """
    The long-term average gas target per block.

    The current gas limit is replaced by two values:
    * a “long-term average target” (equal to the current gas limit) == gas target
    * a “hard per-block cap” (twice the current gas limit) == gas limit

    EIP-1559 gas limit = gas_target * ELASTICITY_MULTIPLIER
    
    See ASSUMPTIONS.md doc for further details about default value assumption.
    """


# Initialize Parameters instance with default values
parameters = Parameters().__dict__
