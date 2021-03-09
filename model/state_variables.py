initial_state = {    
    # Ethereum system
    # NOTE for states that are either dependent on parameters for initialization, or are stochastic processes, is initializing them here to zero and in state update function intuitive?
    # NOTE one option: distinction of initial state vs. state variables, with state_variables.update(initial_state)
    'eth_price': 0, # Units: $/ETH
    'eth_supply':  112_000_000, # Units: ETH
    'eth_staked': 0, # Units: ETH

    # Validators
    'validator_average_effective_balance': 0, # Units: ETH
    # NOTE See comment above re. initialization
    # Initialized in state update function
    'number_of_validators': 0,
    'number_of_validators_online': 0,
    'number_of_validators_offline': 0,
}
