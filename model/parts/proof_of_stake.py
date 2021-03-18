import math
import model.constants as constants


def update_base_reward(params, substep, state_history, previous_state, policy_input):
    '''
    Calculate and update base reward state variable
    '''

    # Parameters
    max_effective_balance = params['MAX_EFFECTIVE_BALANCE']
    base_reward_factor = params['BASE_REWARD_FACTOR']
    base_rewards_per_epoch = params['BASE_REWARDS_PER_EPOCH']

    # State Variables
    eth_staked = previous_state['eth_staked']

    # Policy Signals
    average_effective_balance = policy_input['average_effective_balance']
    
    # Calculate base reward
    base_reward_per_validator = (min(average_effective_balance, max_effective_balance) * base_reward_factor) \
        // math.sqrt(eth_staked * constants.gwei) \
        // base_rewards_per_epoch
    
    return 'base_reward', base_reward_per_validator

def policy_penalties(params, substep, state_history, previous_state):
    base_reward = previous_state['base_reward']
    number_of_validators_offline = previous_state['number_of_validators_offline']

    validating_penalties = base_reward * number_of_validators_offline * 3

    return {
        'validating_penalties': validating_penalties
    }

def update_validating_penalties(params, substep, state_history, previous_state, policy_input):
    return 'validating_penalties', policy_input['validating_penalties']

def policy_casper_ffg_vote(params, substep, state_history, previous_state):
    base_reward = previous_state['base_reward']
    number_of_validators = previous_state['number_of_validators']
    validators_offline_pct = previous_state['number_of_validators_offline'] / number_of_validators

    source_reward = (1 - validators_offline_pct) * base_reward * number_of_validators
    target_reward = source_reward

    return {
        'source_reward': source_reward,
        'target_reward': target_reward,
    }

def policy_lmd_ghost_vote(params, substep, state_history, previous_state):
    proposer_reward_quotient = params['PROPOSER_REWARD_QUOTIENT']

    base_reward = previous_state['base_reward']
    number_of_validators = previous_state['number_of_validators']
    validators_offline_pct = previous_state['number_of_validators_offline'] / number_of_validators

    head_reward = (1 - validators_offline_pct) * base_reward * number_of_validators

    # Inclusion delay reward
    block_attester_reward = (1 - 1 / proposer_reward_quotient) * base_reward * (1 - validators_offline_pct) \
        * (math.log(1 - validators_offline_pct) / ((1 - validators_offline_pct) - 1) * number_of_validators)
    
    return {
        'head_reward': head_reward,
        'block_attester_reward': block_attester_reward,
    }

def policy_block_proposal(params, substep, state_history, previous_state):
    proposer_reward_quotient = params['PROPOSER_REWARD_QUOTIENT']

    base_reward = previous_state['base_reward']
    number_of_validators = previous_state['number_of_validators']
    validators_offline_pct = previous_state['number_of_validators_offline'] / number_of_validators
    
    # See derivation: https://github.com/hermanjunge/eth2-reward-simulation/blob/master/assumptions.md#attester-incentives
    block_proposer_reward = (1 / proposer_reward_quotient) * base_reward * (1 - validators_offline_pct) \
        * (math.log(1 - validators_offline_pct) / ((1 - validators_offline_pct) - 1) * number_of_validators)
    
    return {
        'block_proposer_reward': block_proposer_reward
    }

def update_block_proposer_reward(params, substep, state_history, previous_state, policy_input):
    return 'block_proposer_reward', policy_input['block_proposer_reward']

def update_block_attester_reward(params, substep, state_history, previous_state, policy_input):
    return 'block_attester_reward', policy_input['block_attester_reward']

def update_source_reward(params, substep, state_history, previous_state, policy_input):
    return 'source_reward', policy_input['source_reward']

def update_target_reward(params, substep, state_history, previous_state, policy_input):
    return 'target_reward', policy_input['target_reward']

def update_head_reward(params, substep, state_history, previous_state, policy_input):
    return 'head_reward', policy_input['head_reward']

def update_validating_rewards(params, substep, state_history, previous_state, policy_input):
    block_proposer_reward = policy_input['block_proposer_reward']
    block_attester_reward = policy_input['block_attester_reward']

    source_reward = policy_input['source_reward']
    target_reward = policy_input['target_reward']
    head_reward = policy_input['head_reward']

    validating_rewards = block_proposer_reward + block_attester_reward + source_reward + target_reward + head_reward
    return 'validating_rewards', validating_rewards
