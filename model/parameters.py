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
    Gwei_per_Gas,
    ETH,
    USD_per_epoch,
    Percentage_per_epoch,
    ValidatorType,
    TypedDict,
    List,
    Callable,
    Epoch,
)


class Parameters(TypedDict, total=True):
    # Timescale delta time
    dt: List[Epoch]

    # Environmental processes
    eth_price_process: List[Callable[[Run, Timestep], ETH]]
    eth_staked_process: List[Callable[[Run, Timestep], ETH]]
    validator_process: List[Callable[[Run, Timestep], int]]  # New validators per epoch

    # Parameters from the Eth2 specification
    # Uppercase used for all parameters from Eth2 specification
    BASE_REWARD_FACTOR: List[int]
    BASE_REWARDS_PER_EPOCH: List[int]
    """Example class variable description for the base rewards per epoch"""
    MAX_EFFECTIVE_BALANCE: List[Gwei]
    EFFECTIVE_BALANCE_INCREMENT: List[int]
    SLOTS_PER_EPOCH: List[int]
    SYNC_COMMITTEE_SIZE: List[int]
    PROPOSER_REWARD_QUOTIENT: List[int]
    WHISTLEBLOWER_REWARD_QUOTIENT: List[int]
    MIN_SLASHING_PENALTY_QUOTIENT: List[int]
    TIMELY_HEAD_WEIGHT: List[int]
    TIMELY_SOURCE_WEIGHT: List[int]
    TIMELY_TARGET_WEIGHT: List[int]
    SYNC_REWARD_WEIGHT: List[int]
    PROPOSER_WEIGHT: List[int]
    WEIGHT_DENOMINATOR: List[int]
    MIN_PER_EPOCH_CHURN_LIMIT: List[int]
    CHURN_LIMIT_QUOTIENT: List[int]
    MAX_SEED_LOOKAHEAD: List[int]

    # Validator parameters
    validator_internet_uptime: List[Percentage]
    validator_power_uptime: List[Percentage]
    validator_technical_uptime: List[Percentage]
    validator_percentage_distribution: List[np.ndarray]
    validator_hardware_costs_per_epoch: List[np.ndarray]
    validator_cloud_costs_per_epoch: List[np.ndarray]
    validator_third_party_costs_per_epoch: List[np.ndarray]
    """Percentage of total online validator rewards"""

    # Rewards, penalties, and slashing
    slashing_events_per_1000_epochs: List[int]
    number_of_validating_penalties: List[int]

    # EIP1559
    eip1559_basefee: List[Gwei_per_Gas]
    eip1559_avg_tip_amount: List[Gwei_per_Gas]
    eip1559_avg_transactions_per_day: List[int]
    eip1559_avg_gas_per_transaction: List[Gas]


# Configure environmental ETH price and ETH staking processes
# See https://stochastic.readthedocs.io/en/latest/continuous.html
# Create Random Number Generator (RNG) with a seed of 1
rng = np.random.default_rng(1)
eth_price_process = processes.continuous.BrownianExcursion(
    t=(simulation.TIMESTEPS * simulation.DELTA_TIME), rng=rng
)
eth_price_samples = eth_price_process.sample(
    simulation.TIMESTEPS * simulation.DELTA_TIME + 1
)
eth_staked_samples = np.linspace(
    524_288, 33_600_000, simulation.TIMESTEPS * simulation.DELTA_TIME + 1
)

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
for validator in validator_types:
    validator.percentage_distribution /= total_percentage_distribution

# Parameters from the Eth2 specification
eth2_spec_parameters = {
    "BASE_REWARD_FACTOR": [64],
    "BASE_REWARDS_PER_EPOCH": [4],
    "MAX_EFFECTIVE_BALANCE": [32 * constants.gwei],
    "EFFECTIVE_BALANCE_INCREMENT": [1 * constants.gwei],
    "PROPOSER_REWARD_QUOTIENT": [8],
    "WHISTLEBLOWER_REWARD_QUOTIENT": [512],
    "MIN_SLASHING_PENALTY_QUOTIENT": [2 ** 6],
    "MIN_PER_EPOCH_CHURN_LIMIT": [2 ** 2],
    "MAX_SEED_LOOKAHEAD": [2 ** 2],
    "CHURN_LIMIT_QUOTIENT": [2 ** 16],
    "TIMELY_HEAD_WEIGHT": [12],
    "TIMELY_SOURCE_WEIGHT": [12],
    "TIMELY_TARGET_WEIGHT": [24],
    "SYNC_REWARD_WEIGHT": [8],
    "PROPOSER_WEIGHT": [8],
    "WEIGHT_DENOMINATOR": [64],
    "SLOTS_PER_EPOCH": [32],
    "SYNC_COMMITTEE_SIZE": [2 ** 10],
}

# Configure parameters and parameter sweeps
parameters = Parameters(
    # Unpack the Eth2 spec parameters into the Parameters class initialization
    **eth2_spec_parameters,
    dt=[simulation.DELTA_TIME],
    eth_price_process=[
        lambda _run, timestep: 1000
        + eth_price_samples[timestep] / max(eth_price_samples) * 1000
    ],
    eth_staked_process=[lambda _run, _timestep: None],
    validator_process=[
        lambda _run, timestep: 4
    ],  # From https://beaconscan.com/ as of 20/04/21
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
    validator_third_party_costs_per_epoch=[
        np.array(
            [validator.third_party_costs_per_epoch for validator in validator_types],
            dtype=Percentage_per_epoch,
        )
    ],
    slashing_events_per_1000_epochs=[1],  # Units: 1 / 1000 epochs
    number_of_validating_penalties=[3],
    # TODO confirm average basefee and tip amount
    eip1559_basefee=[100],  # Gwei per gas
    eip1559_avg_tip_amount=[1],  # Gwei per gas
    eip1559_avg_transactions_per_day=[
        1_400_00
    ],  # From https://etherscan.io/chart/tx as of 20/04/21
    eip1559_avg_gas_per_transaction=[73123],  # Gas
)
