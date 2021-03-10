from model.constants import gwei


initial_state = {    
    # Ethereum system
    # NOTE for states that are either dependent on parameters for initialization, or are stochastic processes, is initializing them here to zero and in state update function intuitive?
    # NOTE one option: distinction of initial state vs. state variables, with state_variables.update(initial_state)
    'eth_price': 0, # Units: $/ETH
    'eth_supply':  112_000_000, # Units: ETH
    'eth_staked': 0, # Units: ETH

    # Validators
    # NOTE Why is average effective balance static?
    'average_effective_balance': 32 * gwei, # Units: ETH
    # NOTE See comment above re. initialization
    # Initialized in state update function
    'number_of_validators': 0,
    'number_of_validators_online': 0,
    'number_of_validators_offline': 0,

    # Rewards and penalties
    # TODO
    'base_reward': 0,
    'penalties': 0,

    'reward_ffg_source': 0,
    'penalty_ffg_source': 0,

    'reward_ffg_target': 0,
    'penalty_ffg_target': 0,

    'reward_ffg_head': 0,
    'penalty_ffg_head': 0,

    # Slashing
    'amount_slashed': 0,
    'whistleblower_rewards': 0,
}
