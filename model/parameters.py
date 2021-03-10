from model.constants import gwei

parameters = {
    # Stochastic processes
    'eth_price_process': [lambda _run, _timestep: 300], # Units: ETH
    'eth_staked_process': [lambda _run, _timestep: 524_288], # Units: ETH

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
    # Slashing
    'WHISTLEBLOWER_REWARD_QUOTIENT': [512],
    'MIN_SLASHING_PENALTY_QUOTIENT': [32],

    # Validator uptime
    'validator_internet_uptime': [0.999], # Units: %
    'validator_power_uptime': [0.999], # Units: %
    'validator_technical_uptime': [0.982], # Units: %

    # Rewards, penalties, and slashing
    'slashing_events_per_1000_epochs': [1], # Units: 1 / 1000 epochs
}
