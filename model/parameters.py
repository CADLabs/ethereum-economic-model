"""
Definition of System Parameters, their types, and default values.

By using a dataclass to represent the System Parameters:
* We can use types for Python type hints
* Set default values
* Ensure that all System Parameters are initialized
"""


import numpy as np
import pandas as pd
from stochastic import processes
from dataclasses import dataclass
import logging
from datetime import datetime

import model.simulation_configuration as simulation
import model.constants as constants
from model.types import (
    Run,
    Timestep,
    Percentage,
    Gwei,
    Gas,
    Gwei_per_Gas,
    ETH,
    USD_per_epoch,
    Percentage_per_epoch,
    ValidatorType,
    List,
    Callable,
    Epoch,
    Phase,
)
from model.utils import default


def create_eth_price_process(
    timesteps=simulation.TIMESTEPS, dt=simulation.DELTA_TIME, minimum_eth_price=1500
):
    """Configure environmental ETH price process
    See See https://stochastic.readthedocs.io/en/latest/continuous.html
    """
    # Create Random Number Generator (RNG) with a seed of 1
    rng = np.random.default_rng(1)
    eth_price_process = processes.continuous.BrownianExcursion(
        t=(timesteps * dt), rng=rng
    )
    eth_price_samples = eth_price_process.sample(timesteps * dt + 1)
    maximum_eth_price = max(eth_price_samples)
    eth_price_samples = [
        minimum_eth_price + eth_price_sample / maximum_eth_price * minimum_eth_price
        for eth_price_sample in eth_price_samples
    ]
    return eth_price_samples


# Configure validator type distribution
validator_types = [
    ValidatorType(
        type="diy_hardware",
        percentage_distribution=0.37,
        hardware_costs_per_epoch=0.0014,
    ),
    ValidatorType(
        type="diy_cloud",
        percentage_distribution=0.13,
        cloud_costs_per_epoch=0.00027,
    ),
    ValidatorType(
        type="pool_staas",
        percentage_distribution=0.27,
        third_party_costs_per_epoch=0.12,
    ),
    ValidatorType(
        type="pool_hardware",
        percentage_distribution=0.05,
        hardware_costs_per_epoch=0.0007,
    ),
    ValidatorType(
        type="pool_cloud",
        percentage_distribution=0.02,
        cloud_costs_per_epoch=0.00136,
    ),
    ValidatorType(
        type="staas_full",
        percentage_distribution=0.08,
        third_party_costs_per_epoch=0.15,
    ),
    ValidatorType(
        type="staas_self_custodied",
        percentage_distribution=0.08,
        third_party_costs_per_epoch=0.12,
    ),
]

# Normalise percentage distribution to a total of 100%
total_percentage_distribution = sum(
    [validator.percentage_distribution for validator in validator_types]
)

if total_percentage_distribution < 1:
    logging.warn(
        """
    Parameter validator.percentage_distribution normalized due to sum not being equal to 100%
    """
    )
    for validator in validator_types:
        validator.percentage_distribution /= total_percentage_distribution

# Using list comprehension, map the validator types to each parameter
validator_percentage_distribution = [
    np.array(
        [validator.percentage_distribution for validator in validator_types],
        dtype=Percentage,
    )
]
validator_hardware_costs_per_epoch = [
    np.array(
        [validator.hardware_costs_per_epoch for validator in validator_types],
        dtype=USD_per_epoch,
    )
]
validator_cloud_costs_per_epoch = [
    np.array(
        [validator.cloud_costs_per_epoch for validator in validator_types],
        dtype=USD_per_epoch,
    )
]
validator_third_party_costs_per_epoch = [
    np.array(
        [validator.third_party_costs_per_epoch for validator in validator_types],
        dtype=Percentage_per_epoch,
    )
]


@dataclass
class Parameters:
    """System Parameters
    Each System Parameter is defined as:
    system parameter key: system parameter type = default system parameter value

    Because lists are mutable, we need to wrap each parameter list in the `default(...)` method.
    """

    # Time parameters
    dt: List[Epoch] = default([simulation.DELTA_TIME])
    """Simulation timescale / timestep unit of time"""

    phase: List[Phase] = default([Phase.POST_MERGE])
    """Which phase or phases of the network upgrade process to simulate"""

    date_start: List[datetime] = default([datetime.now()])
    """Start date for simulation as Python datetime"""

    date_eip1559: List[datetime] = default(
        [datetime.strptime("2021/07/14", "%Y/%m/%d")]
    )
    """
    EIP1559 activation date as Python datetime
    Source: https://github.com/ethereum/pm/issues/245#issuecomment-825751460
    """

    date_merge: List[datetime] = default([datetime.strptime("2021/12/1", "%Y/%m/%d")])
    """
    Eth1/Eth2 merge date as Python datetime
    Source: https://twitter.com/drakefjustin/status/1379052831982956547
    """

    # Environmental processes
    eth_price_process: List[Callable[[Run, Timestep], ETH]] = default(
        [lambda _run, timestep: eth_price_samples[timestep]]
    )
    """ETH spot price at each epoch"""

    eth_staked_process: List[Callable[[Run, Timestep], ETH]] = default(
        [lambda _run, _timestep: None]
    )
    """ETH staked at each epoch"""

    validator_process: List[Callable[[Run, Timestep], int]] = default(
        [
            # From https://beaconscan.com/statistics as of 20/04/21
            lambda _run, timestep: 3
        ]
    )
    """New validators per epoch (used if model not driven using eth_staked_process)"""

    # Ethereum system parameters
    daily_pow_issuance: List[ETH] = default([13_550])
    """
    Average daily Proof of Work issuance in ETH
    Source: https://etherscan.io/chart/blockreward
    """

    # Parameters from the Eth2 specification
    # Uppercase used for all parameters from Eth2 specification
    BASE_REWARD_FACTOR: List[int] = default([64])
    MAX_EFFECTIVE_BALANCE: List[Gwei] = default([32 * constants.gwei])
    EFFECTIVE_BALANCE_INCREMENT: List[Gwei] = default([1 * constants.gwei])
    PROPOSER_REWARD_QUOTIENT: List[int] = default([8])
    WHISTLEBLOWER_REWARD_QUOTIENT: List[int] = default([512])
    MIN_SLASHING_PENALTY_QUOTIENT: List[int] = default([2 ** 6])
    TIMELY_HEAD_WEIGHT: List[int] = default([12])
    TIMELY_SOURCE_WEIGHT: List[int] = default([12])
    TIMELY_TARGET_WEIGHT: List[int] = default([24])
    SYNC_REWARD_WEIGHT: List[int] = default([8])
    PROPOSER_WEIGHT: List[int] = default([8])
    WEIGHT_DENOMINATOR: List[int] = default([64])
    MIN_PER_EPOCH_CHURN_LIMIT: List[int] = default([4])
    CHURN_LIMIT_QUOTIENT: List[int] = default([2 ** 16])
    BASE_FEE_MAX_CHANGE_DENOMINATOR: List[int] = default([8])

    # Validator parameters
    validator_uptime: List[Percentage] = default([0.98])
    """Combination of validator internet, power, and technical uptime"""
    validator_percentage_distribution: List[np.ndarray] = default(
        validator_percentage_distribution
    )
    validator_hardware_costs_per_epoch: List[np.ndarray] = default(
        validator_hardware_costs_per_epoch
    )
    validator_cloud_costs_per_epoch: List[np.ndarray] = default(
        validator_cloud_costs_per_epoch
    )
    validator_third_party_costs_per_epoch: List[np.ndarray] = default(
        validator_third_party_costs_per_epoch
    )
    """Validator cost as a percentage of total online validator rewards"""

    # Rewards, penalties, and slashing
    slashing_events_per_1000_epochs: List[int] = default([1])  # 1 / 1000 epochs
    """
    Number of slashing events per 1000 epochs. Asssumption from Hoban/Borgers report.
    """

    # EIP1559 transaction pricing parameters
    ELASTICITY_MULTIPLIER: List[int] = default([2])
    """
    Used to calculate gas limit from EIP1559 gas target
    """

    eip1559_basefee_process: List[Callable[[Run, Timestep], Gwei_per_Gas]] = default(
        [lambda _run, _timestep: 70]  # Gwei per gas
    )
    """
    Approximated using average gas price from https://etherscan.io/gastracker as of 20/04/21
    """

    eip1559_tip_process: List[Callable[[Run, Timestep], Gwei_per_Gas]] = default(
        [lambda _run, _timestep: 30]  # Gwei per gas
    )
    """
    The tip level that compensates for uncle risk.
    See https://notes.ethereum.org/@vbuterin/BkSQmQTS8#Why-would-miners-include-transactions-at-all
    """

    gas_target: List[Gas] = default([15e6])
    """
    EIP1559 gas limit = gas_target * ELASTICITY_MULTIPLIER
    See https://eips.ethereum.org/EIPS/eip-1559
    """

    daily_transactions_process: List[int] = default([lambda _run, _timestep: 1_400_000])
    """
    Number of transactions per day.

    fees per day = daily_transactions * transaction_average_gas * (basefee + tip) / 1e9 ~= 10k ETH
    (see https://etherscan.io/chart/transactionfee)
    
    Where:
    * daily_transactions ~= 1_400_000
    * transaction_average_gas ~= 73_123
    * (basefee + tip) ~= 100

    Static default from https://etherscan.io/chart/tx as of 20/04/21
    """

    transaction_average_gas: List[Gas] = default([73_123])
    """Average gas per transaction"""


# Initialize Parameters instance with default values
parameters = Parameters().__dict__
