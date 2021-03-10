import model.constants as constants
from model.constants import gwei


def policy_validators(params, substep, state_history, previous_state):
    # Calculate the net validators uptime
    validators_uptime = params['validator_internet_uptime'] * params['validator_power_uptime'] * params['validator_technical_uptime']

    # Calculate the number of validators using ETH staked
    number_of_validators = previous_state['eth_staked'] / (previous_state['average_effective_balance'] / constants.gwei)

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

def update_average_effective_balance(params, substep, state_history, previous_state, policy_input):
    effective_balance_increment = params['EFFECTIVE_BALANCE_INCREMENT']

    eth_staked = previous_state['eth_staked']
    number_of_validators = previous_state['number_of_validators']
    max_effective_balance = params['MAX_EFFECTIVE_BALANCE']

    # TODO check balance == eth_staked at aggregate
    # TODO confirm effective balance multiplied by both online and offline validators
    average_effective_balance = min(eth_staked * gwei - eth_staked * gwei % effective_balance_increment, max_effective_balance * number_of_validators) / number_of_validators

    return 'average_effective_balance', average_effective_balance
