import numpy as np
import pandas as pd
from stochastic import processes
from dataclasses import dataclass, field
import logging

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
from model.utils import default


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
    logging.warn("""
    Parameter validator.percentage_distribution normalized due to sum not being equal to 100%
    """)
    for validator in validator_types:
        validator.percentage_distribution /= total_percentage_distribution


@dataclass
class Parameters:
    dt: List[Epoch] = default([simulation.DELTA_TIME])
    """Simulation timescale / timestep unit of time"""

    # Environmental processes
    eth_price_process: List[Callable[[Run, Timestep], ETH]] = default([
        lambda _run, timestep: 1000
        + eth_price_samples[timestep] / max(eth_price_samples) * 1000
    ])
    """ETH spot price at each epoch"""

    eth_staked_process: List[Callable[[Run, Timestep], ETH]] = default([
        lambda _run, _timestep: None
    ])
    """ETH staked at each epoch"""

    validator_process: List[Callable[[Run, Timestep], int]] = default([
        
        # From https://beaconscan.com/ as of 20/04/21
        lambda _run, timestep: 4
    ])
    """New validators per epoch (enabled if model not driven using eth_staked_process)"""

    # Parameters from the Eth2 specification
    # Uppercase used for all parameters from Eth2 specification
    BASE_REWARD_FACTOR: List[int] = default([64])
    MAX_EFFECTIVE_BALANCE: List[Gwei] = default([32 * constants.gwei])
    EFFECTIVE_BALANCE_INCREMENT: List[int] = default([1 * constants.gwei])
    SLOTS_PER_EPOCH: List[int] = default([32])
    SYNC_COMMITTEE_SIZE: List[int] = default([2 ** 10])
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

    # Validator parameters
    validator_internet_uptime: List[Percentage] = default([0.999])
    validator_power_uptime: List[Percentage] = default([0.999])
    validator_technical_uptime: List[Percentage] = default([0.982])

    # Using list comprehension, map the validator types to each parameter
    validator_percentage_distribution: List[np.ndarray] = default([
        np.array(
            [validator.percentage_distribution for validator in validator_types],
            dtype=Percentage,
        )
    ])
    validator_hardware_costs_per_epoch: List[np.ndarray] = default([
        np.array(
            [validator.hardware_costs_per_epoch for validator in validator_types],
            dtype=USD_per_epoch,
        )
    ])
    validator_cloud_costs_per_epoch: List[np.ndarray] = default([
        np.array(
            [validator.cloud_costs_per_epoch for validator in validator_types],
            dtype=USD_per_epoch,
        )
    ])
    validator_third_party_costs_per_epoch: List[np.ndarray] = default([
        np.array(
            [validator.third_party_costs_per_epoch for validator in validator_types],
            dtype=Percentage_per_epoch,
        )
    ])
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

    eip1559_avg_basefee: List[Gwei_per_Gas] = default([50])  # Gwei per gas
    """
    Approximated using average gas price from https://etherscan.io/gastracker as of 20/04/21
    """

    eip1559_avg_tip_amount: List[Gwei_per_Gas] = default([1])  # Gwei per gas
    """
    The tip level that compensates for uncle risk.
    See https://notes.ethereum.org/@vbuterin/BkSQmQTS8#Why-would-miners-include-transactions-at-all
    """

    gas_target: List[Gas] = default([15e6])
    """
    EIP1559 gas limit = gas_target * ELASTICITY_MULTIPLIER
    See https://eips.ethereum.org/EIPS/eip-1559
    """


# Initialize Parameters instance with default values
parameters = Parameters().__dict__
