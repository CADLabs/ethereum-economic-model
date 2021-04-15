import numpy as np
import pandas as pd
from stochastic import processes

import model.simulation_configuration as simulation
import model.constants as constants
from model.types import (
    Run,
    Timestep,
    Percentage,
    Gwei,
    Gas,
    ETH,
    USD_per_epoch,
    Percentage_per_epoch,
    ValidatorType,
    TypedDict,
    List,
    Callable,
)


class Parameters(TypedDict, total=True):
    # Stochastic processes
    eth_price_process: List[Callable[[Run, Timestep], ETH]]
    eth_staked_process: List[Callable[[Run, Timestep], ETH]]

    # See blueprint model 'Variables and Model Assumptions'
    # Uppercase used for all parameters from Eth2 specification
    BASE_REWARD_FACTOR: List[int]
    BASE_REWARDS_PER_EPOCH: List[int]

    MAX_EFFECTIVE_BALANCE: List[Gwei]
    EFFECTIVE_BALANCE_INCREMENT: List[int]
    SLOTS_PER_EPOCH: List[int]
    SYNC_COMMITTEE_SIZE: List[int]

    # Rewards and penalties
    PROPOSER_REWARD_QUOTIENT: List[int]
    WHISTLEBLOWER_REWARD_QUOTIENT: List[int]
    MIN_SLASHING_PENALTY_QUOTIENT: List[int]
    TIMELY_HEAD_WEIGHT: List[int]
    TIMELY_SOURCE_WEIGHT: List[int]
    TIMELY_TARGET_WEIGHT: List[int]
    SYNC_REWARD_WEIGHT: List[int]
    PROPOSER_WEIGHT: List[int]
    WEIGHT_DENOMINATOR: List[int]

    # Validator parameters
    validator_internet_uptime: List[Percentage]
    validator_power_uptime: List[Percentage]
    validator_technical_uptime: List[Percentage]
    validator_percentage_distribution: List[np.ndarray]
    validator_hardware_costs_per_epoch: List[np.ndarray]
    validator_cloud_costs_per_epoch: List[np.ndarray]
    validator_third_party_costs_per_epoch: List[np.ndarray]

    # Rewards, penalties, and slashing
    slashing_events_per_1000_epochs: List[int]
    number_of_validating_penalties: List[int]

    # EIP1559
    eip1559_basefee: List[Gwei]
    eip1559_avg_tip_amount: List[Percentage]
    eip1559_avg_transactions_per_day: List[int]
    eip1559_avg_gas_per_transaction: List[Gas]


# Configure stochastic ETH price and staking processes
# See https://stochastic.readthedocs.io/en/latest/continuous.html
# Create Random Number Generator (RNG) with a seed of 1
rng = np.random.default_rng(1)
eth_price_process = processes.continuous.BrownianExcursion(
    t=simulation.TIMESTEPS, rng=rng
)
eth_price_samples = eth_price_process.sample(simulation.TIMESTEPS)
eth_staked_samples = np.linspace(524_288, 33_600_000, simulation.TIMESTEPS)

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
total_percentage_distribution = sum([
    validator.percentage_distribution for validator in validator_types
])
for validator in validator_types:
    validator.percentage_distribution /= total_percentage_distribution

# Configure parameters and parameter sweeps
parameters = Parameters(
    eth_price_process=[
        lambda _run, timestep: 1000
        + eth_price_samples[timestep] / max(eth_price_samples) * 1000
    ],
    eth_staked_process=[lambda _run, timestep: eth_staked_samples[timestep]],
    BASE_REWARD_FACTOR=[64],
    BASE_REWARDS_PER_EPOCH=[4],
    MAX_EFFECTIVE_BALANCE=[32 * constants.gwei],
    EFFECTIVE_BALANCE_INCREMENT=[1 * constants.gwei],
    PROPOSER_REWARD_QUOTIENT=[8],
    WHISTLEBLOWER_REWARD_QUOTIENT=[512],
    MIN_SLASHING_PENALTY_QUOTIENT=[2 ** 6],
    TIMELY_HEAD_WEIGHT=[12],
    TIMELY_SOURCE_WEIGHT=[12],
    TIMELY_TARGET_WEIGHT=[24],
    SYNC_REWARD_WEIGHT=[8],
    PROPOSER_WEIGHT=[8],
    WEIGHT_DENOMINATOR=[64],
    SLOTS_PER_EPOCH=[32],
    SYNC_COMMITTEE_SIZE=[2 ** 10],
    validator_internet_uptime=[0.999],
    validator_power_uptime=[0.999],
    validator_technical_uptime=[0.982],
    # Using list comprehension, map the validator types to each parameter
    validator_percentage_distribution=[
        np.array(
            [validator.percentage_distribution for validator in validator_types],
            dtype=Percentage,
        )
    ],
    validator_hardware_costs_per_epoch=[
        np.array(
            [validator.hardware_costs_per_epoch for validator in validator_types],
            dtype=USD_per_epoch,
        )
    ],
    validator_cloud_costs_per_epoch=[
        np.array(
            [validator.cloud_costs_per_epoch for validator in validator_types],
            dtype=USD_per_epoch,
        )
    ],
    # Percentage of total online validator rewards
    validator_third_party_costs_per_epoch=[
        np.array(
            [validator.third_party_costs_per_epoch for validator in validator_types],
            dtype=Percentage_per_epoch,
        )
    ],
    slashing_events_per_1000_epochs=[1],  # Units: 1 / 1000 epochs
    number_of_validating_penalties=[3],
    # TODO determine basefee and tip amount process or average
    eip1559_basefee=[0],  # Default: 1 * constants.gwei
    eip1559_avg_tip_amount=[0],  # Default: 0.01
    eip1559_avg_transactions_per_day=[688078],
    eip1559_avg_gas_per_transaction=[73123],
)
