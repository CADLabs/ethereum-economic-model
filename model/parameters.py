import numpy as np
import pandas as pd
from stochastic import processes

import model.simulation as simulation
from model.constants import gwei


# See https://stochastic.readthedocs.io/en/latest/continuous.html
rng = np.random.default_rng(1)

eth_price_process = processes.continuous.BrownianExcursion(t=simulation.TIMESTEPS, rng=rng)

eth_price_samples = eth_price_process.sample(simulation.TIMESTEPS)
eth_staked_samples = np.linspace(524_288, 33_600_000, simulation.TIMESTEPS)

parameters = {
    # Stochastic processes
    'eth_price_process': [lambda _run, timestep: 1000 + eth_price_samples[timestep] / max(eth_price_samples) * 1000], # Units: ETH
    'eth_staked_process': [lambda _run, timestep: eth_staked_samples[timestep]], # Units: ETH

    # See blueprint model 'Variables and Model Assumptions'
    # Uppercase used for all parameters from Eth2 specification
    'BASE_REWARD_FACTOR': [64],
    'BASE_REWARDS_PER_EPOCH': [4],
    'MAX_COMMITTEES_PER_SLOT': [64],
    'TARGET_COMMITTEE_SIZE':  [128],
    'MAX_VALIDATORS_PER_COMMITTEE':  [2048],
    'MAX_EFFECTIVE_BALANCE':  [32 * gwei], # Units: Gwei
    'SLOTS_PER_EPOCH': [32], # Units: slots
    'EFFECTIVE_BALANCE_INCREMENT': [1 * gwei], # Units: Gwei
    # Rewards
    'PROPOSER_REWARD_QUOTIENT': [8],
    # Slashing
    'WHISTLEBLOWER_REWARD_QUOTIENT': [512],
    'MIN_SLASHING_PENALTY_QUOTIENT': [32],

    # Validator uptime
    'validator_internet_uptime': [0.999], # Units: %
    'validator_power_uptime': [0.999], # Units: %
    'validator_technical_uptime': [0.982], # Units: %

    # Rewards, penalties, and slashing
    'slashing_events_per_1000_epochs': [1], # Units: 1 / 1000 epochs

    # EIP1559
    'eip1559_basefee': [5e9], # Units: Gwei
    'eip1559_avg_tip_amount': [1e9], # Units: Gwei
    'eip1559_avg_transactions_per_day': [688078],
    'eip1559_avg_gas_per_transaction': [73123], # Units: Gas
}
