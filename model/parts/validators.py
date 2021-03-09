import model.constants as constants


def policy_validators(params, substep, state_history, previous_state):
    # Calculate the net validators uptime
    validators_uptime = params['validator_internet_uptime'] * params['validator_power_uptime'] * params['validator_technical_uptime']

    # Calculate the number of validators using ETH staked
    number_of_validators = previous_state['eth_staked'] / (constants.average_effective_balance / constants.gwei)

    # Calculate the number of validators online and offline using validators uptime
    number_of_validators_online = number_of_validators * validators_uptime
    number_of_validators_offline = number_of_validators - number_of_validators_online

    return {
        'number_of_validators': number_of_validators,
        'number_of_validators_online': number_of_validators_online,
        'number_of_validators_offline': number_of_validators_offline,
    }

def update_number_of_validators(params, substep, state_history, previous_state, policy_input):
    return 'number_of_validators', policy_input['number_of_validators']

def update_number_of_validators_online(params, substep, state_history, previous_state, policy_input):
    return 'number_of_validators_online', policy_input['number_of_validators_online']

def update_number_of_validators_offline(params, substep, state_history, previous_state, policy_input):
    return 'number_of_validators_offline', policy_input['number_of_validators_offline']
