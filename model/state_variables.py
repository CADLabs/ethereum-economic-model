from model.constants import gwei


initial_state = {    
    # Ethereum system
    # NOTE for states that are either dependent on parameters for initialization, or are stochastic processes, is initializing them here to zero and in state update function intuitive?
    # NOTE one option: distinction of initial state vs. state variables, with state_variables.update(initial_state)
    'eth_price': 0, # Units: $/ETH
    'eth_supply':  112_000_000, # Units: ETH
    'eth_staked': 0, # Units: ETH

    'supply_inflation': 0, # Units: %

    # Validators
    # NOTE Why is average effective balance static?
    'average_effective_balance': 32 * gwei, # Units: ETH
    # NOTE See comment above re. initialization
    # Initialized in state update function
    'number_of_validators': 0,
    'number_of_validators_online': 0,
    'number_of_validators_offline': 0,

    # Rewards and penalties
    'validating_rewards': 0,
    'base_reward': 0,
    'penalties': 0,

    # Casper FFG vote
    'ffg_source_reward': 0,
    'ffg_target_reward': 0,

    # LMD Ghost vote
    'ffg_head_reward': 0,
    'block_attester_reward': 0,
    'block_proposer_reward': 0,

    # Slashing
    'amount_slashed': 0,
    'whistleblower_rewards': 0,

    # Accounting
    'total_revenue': 0,
    'total_profit': 0,
    'revenue_yields': 0,
    'profit_yields': 0,

    # EIP1559
    'total_basefee': 0,
    'total_tips_to_validators': 0,
}
