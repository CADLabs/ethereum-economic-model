import math
from model.constants import gwei


def update_base_reward(params, substep, state_history, previous_state, policy_input):
    max_effective_balance = params['MAX_EFFECTIVE_BALANCE']
    base_reward_factor = params['BASE_REWARD_FACTOR']
    base_rewards_per_epoch = params['BASE_REWARDS_PER_EPOCH']

    eth_staked = previous_state['eth_staked']
    average_effective_balance = previous_state['average_effective_balance']
    
    base_reward_per_validator = min(average_effective_balance, max_effective_balance) * base_reward_factor \
        / math.sqrt(eth_staked * gwei) \
        / base_rewards_per_epoch
    
    return 'base_reward', base_reward_per_validator

def policy_penalties(params, substep, state_history, previous_state):
    base_reward = previous_state['base_reward']
    number_of_validators_offline = previous_state['number_of_validators_offline']

    penalties = base_reward * number_of_validators_offline * 3

    return {
        'penalties': penalties
    }

def update_penalties(params, substep, state_history, previous_state, policy_input):
    return 'penalties', policy_input['penalties']
