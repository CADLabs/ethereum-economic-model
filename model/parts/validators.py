import model.constants as constants
from model.parameters import Parameters


def policy_staking(params, substep, state_history, previous_state):
    staked_eth = params['eth_staked_process'](previous_state['run'], previous_state['timestep']) - previous_state['eth_staked']

    return {
        'staked_eth': staked_eth
    }

def policy_validators(params, substep, state_history, previous_state):
    # Calculate the net validators uptime
    validators_uptime = params['validator_internet_uptime'] * params['validator_power_uptime'] * params['validator_technical_uptime']

    # Calculate the number of validators using ETH staked
    number_of_validators = previous_state['eth_staked'] / (previous_state['average_effective_balance'] / constants.gwei)

    # Calculate the number of validators online and offline using validators uptime
    number_of_validators_online = number_of_validators * validators_uptime
    number_of_validators_offline = number_of_validators - number_of_validators_online

    # TODO check int type
    return {
        'number_of_validators': number_of_validators,
        'number_of_validators_online': number_of_validators_online,
        'number_of_validators_offline': number_of_validators_offline,
    }

def policy_average_effective_balance(params, substep, state_history, previous_state):
    effective_balance_increment = params['EFFECTIVE_BALANCE_INCREMENT']
    max_effective_balance = params['MAX_EFFECTIVE_BALANCE']

    eth_staked = previous_state['eth_staked']
    number_of_validators = previous_state['number_of_validators']

    # TODO check balance == eth_staked at aggregate
    # TODO confirm effective balance multiplied by both online and offline validators
    average_effective_balance = min(eth_staked * constants.gwei - eth_staked * constants.gwei % effective_balance_increment, max_effective_balance * number_of_validators) / number_of_validators

    return {'average_effective_balance': average_effective_balance}

def update_number_of_validators(params, substep, state_history, previous_state, policy_input):
    return 'number_of_validators', policy_input['number_of_validators']

def update_number_of_validators_online(params, substep, state_history, previous_state, policy_input):
    return 'number_of_validators_online', policy_input['number_of_validators_online']

def update_number_of_validators_offline(params, substep, state_history, previous_state, policy_input):
    return 'number_of_validators_offline', policy_input['number_of_validators_offline']

def update_average_effective_balance(params, substep, state_history, previous_state, policy_input):
    return 'average_effective_balance', policy_input['average_effective_balance']
