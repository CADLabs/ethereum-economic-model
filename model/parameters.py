import numpy as np
import pandas as pd
from stochastic import processes
from typing import TypedDict, List, Callable

import model.simulation as simulation
import model.constants as constants
from model.types import Run, Timestep, Percentage, Gwei, Gas, ETH


# See https://stochastic.readthedocs.io/en/latest/continuous.html
rng = np.random.default_rng(1)

eth_price_process = processes.continuous.BrownianExcursion(t=simulation.TIMESTEPS, rng=rng)

eth_price_samples = eth_price_process.sample(simulation.TIMESTEPS)
eth_staked_samples = np.linspace(524_288, 33_600_000, simulation.TIMESTEPS)


class Parameters(TypedDict, total=True):
    # Stochastic processes
    eth_price_process: List[Callable[[Run, Timestep], ETH]]
    eth_staked_process: List[Callable[[Run, Timestep], ETH]]

    # See blueprint model 'Variables and Model Assumptions'
    # Uppercase used for all parameters from Eth2 specification
    BASE_REWARD_FACTOR: List[int]
    BASE_REWARDS_PER_EPOCH: List[int]

    MAX_COMMITTEES_PER_SLOT: List[int]
    TARGET_COMMITTEE_SIZE: List[int]
    MAX_VALIDATORS_PER_COMMITTEE: List[int]
    MAX_EFFECTIVE_BALANCE: List[Gwei]
    SLOTS_PER_EPOCH: List[int]
    EFFECTIVE_BALANCE_INCREMENT: List[int]

    # Rewards and penalties
    PROPOSER_REWARD_QUOTIENT: List[int]
    WHISTLEBLOWER_REWARD_QUOTIENT: List[int]
    MIN_SLASHING_PENALTY_QUOTIENT: List[int]

    # Validator uptime
    validator_internet_uptime: List[Percentage]
    validator_power_uptime: List[Percentage]
    validator_technical_uptime: List[Percentage]

    # Rewards, penalties, and slashing
    slashing_events_per_1000_epochs: List[int]

    # EIP1559
    eip1559_basefee: List[Gwei]
    eip1559_avg_tip_amount: List[Gwei]
    eip1559_avg_transactions_per_day: List[int]
    eip1559_avg_gas_per_transaction: List[Gas]


parameters: Parameters = {
    'eth_price_process': [lambda _run, timestep: 1000 + eth_price_samples[timestep] / max(eth_price_samples) * 1000],
    'eth_staked_process': [lambda _run, timestep: eth_staked_samples[timestep]],

    'BASE_REWARD_FACTOR': [64],
    'BASE_REWARDS_PER_EPOCH': [4],
    'MAX_COMMITTEES_PER_SLOT': [64],
    'TARGET_COMMITTEE_SIZE':  [128],
    'MAX_VALIDATORS_PER_COMMITTEE':  [2048],
    'MAX_EFFECTIVE_BALANCE':  [32 * constants.gwei],
    'SLOTS_PER_EPOCH': [32], # Units: slots
    'EFFECTIVE_BALANCE_INCREMENT': [1 * constants.gwei],
    'PROPOSER_REWARD_QUOTIENT': [8],
    'WHISTLEBLOWER_REWARD_QUOTIENT': [512],
    'MIN_SLASHING_PENALTY_QUOTIENT': [32],

    'validator_internet_uptime': [0.999],
    'validator_power_uptime': [0.999],
    'validator_technical_uptime': [0.982],

    'slashing_events_per_1000_epochs': [1], # Units: 1 / 1000 epochs

    'eip1559_basefee': [0],
    'eip1559_avg_tip_amount': [0],
    'eip1559_avg_transactions_per_day': [688078],
    'eip1559_avg_gas_per_transaction': [73123],
}
