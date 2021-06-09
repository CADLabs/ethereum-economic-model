"""
Definition of System Parameters, their types, and default values.

By using a dataclass to represent the System Parameters:
* We can use types for Python type hints
* Set default values
* Ensure that all System Parameters are initialized
"""


import numpy as np
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
    ValidatorEnvironment,
    List,
    Callable,
    Epoch,
    Stage,
)
from model.utils import default
from model.processes import create_stochastic_process_realizations


# Create stochastic (random) process realizations
stochastic_process_realizations = create_stochastic_process_realizations()
eth_price_samples = stochastic_process_realizations["eth_price_samples"]

# Configure validator environment distribution
validator_environments = [
    ValidatorEnvironment(
        # Configure a custom environment
        # Used for dissagregation of single validator performance
        type="custom",
        percentage_distribution=0.01,  # Set to 1% by default
        hardware_costs_per_epoch=0.0014,
        cloud_costs_per_epoch=0,
        third_party_costs_per_epoch=0,
    ),
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

From the Hoban/Borgers report (Ethereum 2.0 Economic Review):
> assume validators will consider different validator models according to their preferences, requirements, and the scale of their stake
> The breakdown of validator environments reflects the results of user surveys and stakeholder interviews

Cost analysis:
> See "Ethereum 2.0 Ecosystem Staking Report" by ConsenSys Insights: https://cdn2.hubspot.net/hubfs/4795067/Codefi/Ethereum%202.0%20Staking%20Ecosystem%20Report.pdf?__hstc=148571112.51d5567256d6f4167c1422d5c083e93e.1574348924308.1588770700176.1588788083651.18&__hssc=148571112.1.1588788083651
> See "Ethereum Lighthouse: Chasing Serenity" survey report by Empire Ventures: https://medium.com/empireventures/eth2uxreport-858c73ca1f53
"""

# Normalise percentage distribution to a total of 100%
total_percentage_distribution = sum(
    [validator.percentage_distribution for validator in validator_environments]
)

if total_percentage_distribution < 1:
    logging.warn(
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
    """

    # Time parameters
    dt: List[Epoch] = default([simulation.DELTA_TIME])
    """
    Simulation timescale / timestep unit of time, in epochs.

    Used to scale calculations that depend on the number of epochs that have passed.

    For example, for dt = 100, each timestep equals 100 epochs.
    
    By default set to constants.epochs_per_day (225)
    """

    stage: List[Stage] = default([Stage.PROOF_OF_STAKE])
    """
    Which stage or stages of the network upgrade process to simulate.

    By default set to PROOF_OF_STAKE stage, where EIP1559 is enabled and POW issuance is disabled.

    See model.types.Stage Enum for further documentation.
    """

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
        [lambda run, timestep: eth_price_samples[run - 1][timestep]]
    )
    """
    A process that returns the ETH spot price at each epoch.
    """

    eth_staked_process: List[Callable[[Run, Timestep], ETH]] = default(
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
            # From https://beaconscan.com/statistics as of 20/04/21
            lambda _run, _timestep: 3,
        ]
    )
    """
    A process that returns the number of new validators per epoch.
    
    Used if model not driven using `eth_staked_process`.

    By default set to a static value from https://beaconscan.com/statistics.
    """

    # Ethereum system parameters
    daily_pow_issuance: List[ETH] = default([13_550])
    """
    The average daily Proof of Work issuance in ETH.

    See https://etherscan.io/chart/blockreward
    """

    # Parameters from the Eth2 specification
    # Uppercase used for all parameters from Eth2 specification
    BASE_REWARD_FACTOR: List[int] = default([64])
    """
    A parameter used to change the issuance rate of the Ethereum PoS system.

    Most validator rewards and penalties are calculated in terms of the base reward.
    """
    MAX_EFFECTIVE_BALANCE: List[Gwei] = default([32 * constants.gwei])
    """
    A validators effective balance is used to calculate incentives, and for voting,
    and is a value less than the total stake/balance.

    The max effective balance of a validator is 32 ETH.
    """
    EFFECTIVE_BALANCE_INCREMENT: List[Gwei] = default([1 * constants.gwei])
    """
    A validators effective balance can only change in steps of EFFECTIVE_BALANCE_INCREMENT,
    which reduces the computational load for state updates.
    """
    PROPOSER_REWARD_QUOTIENT: List[int] = default([8])
    """
    Used to calculate the proportion of rewards distributed between attesters and proposers.
    """
    WHISTLEBLOWER_REWARD_QUOTIENT: List[int] = default([512])
    """
    Used to calculate the proportion of the effective balance of the slashed validator
    distributed between the whistleblower and the proposer.
    """
    MIN_SLASHING_PENALTY_QUOTIENT: List[int] = default([2 ** 6])
    """
    Used to calculate the penalty applied for a slashable offence.
    """
    PROPORTIONAL_SLASHING_MULTIPLIER: List[int] = default([2])
    """
    Scales the slashing penalty proportional to the total slashings for the current epoch

    i.e. the more slashing events there are, the greater the individual penalty
    """
    TIMELY_HEAD_WEIGHT: List[int] = default([12])
    """
    Used to calculate the reward received for getting a head vote in time and correctly.

    `head_reward = (TIMELY_HEAD_WEIGHT / WEIGHT_DENOMINATOR) * base_reward`
    """
    TIMELY_SOURCE_WEIGHT: List[int] = default([12])
    """
    Used to calculate the reward received for getting a source vote in time and correctly.

    `source_reward = (TIMELY_SOURCE_WEIGHT / WEIGHT_DENOMINATOR) * base_reward`
    """
    TIMELY_TARGET_WEIGHT: List[int] = default([24])
    """
    Used to calculate the reward received for getting a target vote in time and correctly.

    `target_reward = (TIMELY_TARGET_WEIGHT / WEIGHT_DENOMINATOR) * base_reward`
    """
    SYNC_REWARD_WEIGHT: List[int] = default([8])
    """
    Used to calculate the reward received for attesting as part of a sync committee.
    """
    PROPOSER_WEIGHT: List[int] = default([8])
    """
    Used to calculate the reward received for successfully proposing a block.
    """
    WEIGHT_DENOMINATOR: List[int] = default([64])
    """
    Used as the denominator in incentive calculations to calculate reward and penalty proportions.
    """
    MIN_PER_EPOCH_CHURN_LIMIT: List[int] = default([4])
    """
    Used to calculate the churn limit for validator entry and exit. The maximum number of validators that can
    enter or exit the system per epoch.
    
    In this system it is used for the validator activation queue process.
    """
    CHURN_LIMIT_QUOTIENT: List[int] = default([2 ** 16])
    """
    Used in the calculation of the churn limit to set a point at which the limit increases.
    """
    BASE_FEE_MAX_CHANGE_DENOMINATOR: List[int] = default([8])
    """
    Used to set the maximum rate at which the EIP1559 basefee can change per block, approx. 12.5%.
    """
    ELASTICITY_MULTIPLIER: List[int] = default([2])
    """
    Used to calculate gas limit from EIP1559 gas target
    """

    # Validator parameters
    validator_uptime_process: List[Percentage] = default(
        [lambda _run, _timestep: max(0.98, 0.666)]
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
    
    Asssumption from Hoban/Borgers report.
    """

    # EIP1559 transaction pricing parameters
    eip1559_basefee_process: List[Callable[[Run, Timestep], Gwei_per_Gas]] = default(
        [lambda _run, _timestep: 70]  # Gwei per gas
    )
    """
    The basefee burned, in Gwei per gas, for each transaction.
    
    An average of 100 Gwei per gas expected to be set as transaction fee cap,
    split between the basefee and tips - the fee cap less the basefee is sent as a tip to miners/validators.

    Approximated using average gas price from https://etherscan.io/gastracker as of 20/04/21

    An extract from https://notes.ethereum.org/@vbuterin/eip-1559-faq
    
    > Each “full block” (ie. a block whose gas is 2x the TARGET) increases the BASEFEE by 1.125x,
    > so a series of constant full blocks will increase the gas price by a factor of 10 every
    > ~20 blocks (~4.3 min on average).
    > Hence, periods of heavy on-chain load will not realistically last longer than ~5 minutes.
    """

    eip1559_tip_process: List[Callable[[Run, Timestep], Gwei_per_Gas]] = default(
        [lambda _run, _timestep: 30]  # Gwei per gas
    )
    """
    EIP1559 transaction pricing tip, in Gwei per gas.
    
    Due to MEV, average tips expected to be higher than usual as bid for inclusion in blockscpace market.
    
    The tip is the difference between the fee cap set per transaction, and the basefee.

    For PoW system without MEV influence, the tip level compensates for uncle risk:
    See https://notes.ethereum.org/@vbuterin/BkSQmQTS8#Why-would-miners-include-transactions-at-all
    """

    gas_target: List[Gas] = default([15e6])
    """
    The long-term average gas target per block.

    The current gas limit is replaced by two values:
    * a “long-term average target” (equal to the current gas limit) == gas target
    * a “hard per-block cap” (twice the current gas limit) == gas limit

    EIP1559 gas limit = gas_target * ELASTICITY_MULTIPLIER
    See https://eips.ethereum.org/EIPS/eip-1559
    """

    daily_transactions_process: List[int] = default(
        [lambda _run=None, _timestep=None: 1_400_000]
    )
    """
    A process that returns the number of transactions per day.

    fees_per_day = daily_transactions * transaction_average_gas * (basefee + tip) / 1e9 ~= 10k ETH
    (see https://etherscan.io/chart/transactionfee)
    
    Where:
    * daily_transactions ~= 1_400_000
    * transaction_average_gas ~= 73_123
    * (basefee + tip) ~= 100

    Default static daily transactions from https://etherscan.io/chart/tx as of 20/04/21
    """

    transaction_average_gas: List[Gas] = default([73_123])
    """
    The average gas used per transaction.

    A simple ETH transfer takes 21,000 gas,
    but executing a trade on a decentralized exchange can cost 100,000 gas or more.

    See https://coinmetrics.io/the-ethereum-gas-report/
    """


# Initialize Parameters instance with default values
parameters = Parameters().__dict__
