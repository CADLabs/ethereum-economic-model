def update_eth_price(params, substep, state_history, previous_state, policy_input):
    eth_price_sample = params['eth_price_process'](previous_state['run'], previous_state['timestep'])
    return 'eth_price', eth_price_sample

def update_eth_staked(params, substep, state_history, previous_state, policy_input):
    eth_staked_sample = params['eth_staked_process'](previous_state['run'], previous_state['timestep'])
    return 'eth_staked', eth_staked_sample
