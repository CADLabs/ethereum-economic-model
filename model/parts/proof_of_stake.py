import math
from model.constants import gwei


def update_base_reward(params, substep, state_history, previous_state, policy_input):
    max_effective_balance = params['MAX_EFFECTIVE_BALANCE']
    base_reward_factor = params['BASE_REWARD_FACTOR']
    base_rewards_per_epoch = params['BASE_REWARDS_PER_EPOCH']

    eth_staked = previous_state['eth_staked']
    average_effective_balance = previous_state['average_effective_balance']
    
    base_reward_per_validator = min(average_effective_balance, max_effective_balance) * base_reward_factor \
        // math.sqrt(eth_staked * gwei) \
        // base_rewards_per_epoch
    
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

def policy_casper_ffg_vote(params, substep, state_history, previous_state):
    base_reward = previous_state['base_reward']
    number_of_validators = previous_state['number_of_validators']
    validators_offline_pct = previous_state['number_of_validators_offline'] / number_of_validators

    ffg_source_reward = (1 - validators_offline_pct) * base_reward * number_of_validators
    ffg_target_reward = ffg_source_reward

    return {
        'ffg_source_reward': ffg_source_reward,
        'ffg_target_reward': ffg_target_reward,
    }

def policy_lmd_ghost_vote(params, substep, state_history, previous_state):
    proposer_reward_quotient = params['PROPOSER_REWARD_QUOTIENT']

    base_reward = previous_state['base_reward']
    number_of_validators = previous_state['number_of_validators']
    validators_offline_pct = previous_state['number_of_validators_offline'] / number_of_validators

    ffg_head_reward = (1 - validators_offline_pct) * base_reward * number_of_validators

    try:
        arg = math.log(1 - validators_offline_pct) / ((1 - validators_offline_pct) - 1)
    except:
        arg = 1

    # Inclusion delay reward
    block_attester_reward = (1 - 1 / proposer_reward_quotient) * base_reward * (1 - validators_offline_pct) \
        * (arg * number_of_validators)
    
    return {
        'ffg_head_reward': ffg_head_reward,
        'block_attester_reward': block_attester_reward,
    }

def policy_block_proposal(params, substep, state_history, previous_state):
    proposer_reward_quotient = params['PROPOSER_REWARD_QUOTIENT']

    base_reward = previous_state['base_reward']
    number_of_validators = previous_state['number_of_validators']
    validators_offline_pct = previous_state['number_of_validators_offline'] / number_of_validators

    try:
        arg = math.log(1 - validators_offline_pct) / ((1 - validators_offline_pct) - 1)
    except:
        arg = 1
    
    block_proposer_reward = (1 / proposer_reward_quotient) * base_reward * (1 - validators_offline_pct) \
        * (arg * number_of_validators)
    
    return {
        'block_proposer_reward': block_proposer_reward
    }

def update_block_proposer_reward(params, substep, state_history, previous_state, policy_input):
    return 'block_proposer_reward', policy_input['block_proposer_reward']

def update_block_attester_reward(params, substep, state_history, previous_state, policy_input):
    return 'block_attester_reward', policy_input['block_attester_reward']

def update_ffg_source_reward(params, substep, state_history, previous_state, policy_input):
    return 'ffg_source_reward', policy_input['ffg_source_reward']

def update_ffg_target_reward(params, substep, state_history, previous_state, policy_input):
    return 'ffg_target_reward', policy_input['ffg_target_reward']

def update_ffg_head_reward(params, substep, state_history, previous_state, policy_input):
    return 'ffg_head_reward', policy_input['ffg_head_reward']

def update_validating_rewards(params, substep, state_history, previous_state, policy_input):
    block_proposer_reward = policy_input['block_proposer_reward']
    block_attester_reward = policy_input['block_attester_reward']

    ffg_source_reward = policy_input['ffg_source_reward']
    ffg_target_reward = policy_input['ffg_target_reward']
    ffg_head_reward = policy_input['ffg_head_reward']

    validating_rewards = block_proposer_reward + block_attester_reward + ffg_source_reward + ffg_target_reward + ffg_head_reward
    return 'validating_rewards', validating_rewards
