import model.constants as constants


def update_eth_price(params, substep, state_history, previous_state, policy_input):
    eth_price_sample = params['eth_price_process'](previous_state['run'], previous_state['timestep'])

    return 'eth_price', eth_price_sample

def update_eth_staked(params, substep, state_history, previous_state, policy_input):
    eth_staked = previous_state['eth_staked']
    staked_eth = policy_input['staked_eth']

    return 'eth_staked', eth_staked + staked_eth

def policy_network_issuance(params, substep, state_history, previous_state):
    amount_slashed = previous_state['amount_slashed']
    total_basefee = previous_state['total_basefee']
    total_tips_to_validators = previous_state['total_tips_to_validators']
    total_online_validator_rewards = previous_state['total_online_validator_rewards']

    network_issuance = total_online_validator_rewards - amount_slashed - total_basefee - total_tips_to_validators
    network_issuance_eth = network_issuance / 1e9

    return {
        'network_issuance': network_issuance,
        'network_issuance_eth': network_issuance_eth,
    }

def update_supply_inflation(params, substep, state_history, previous_state, policy_input):
    eth_supply = previous_state['eth_supply']
    network_issuance_eth = policy_input['network_issuance_eth']

    supply_inflation = (network_issuance_eth * constants.epochs_per_year) / eth_supply
    return 'supply_inflation', supply_inflation

def update_eth_supply(params, substep, state_history, previous_state, policy_input):
    eth_supply = previous_state['eth_supply']
    network_issuance_eth = policy_input['network_issuance_eth']

    return 'eth_supply', eth_supply + network_issuance_eth
