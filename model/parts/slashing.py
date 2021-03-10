def policy_slashing(params, substep, state_history, previous_state):
    whistleblower_reward_quotient = params['WHISTLEBLOWER_REWARD_QUOTIENT']
    min_slashing_penalty_quotient = params['MIN_SLASHING_PENALTY_QUOTIENT']

    average_effective_balance = previous_state['average_effective_balance']
    number_of_slashing_events = params['slashing_events_per_1000_epochs'] / 1000

    amount_slashed = number_of_slashing_events * average_effective_balance / min_slashing_penalty_quotient    
    whistleblower_rewards = average_effective_balance / whistleblower_reward_quotient * number_of_slashing_events

    return {
        'amount_slashed': amount_slashed,
        'whistleblower_rewards': whistleblower_rewards,
    }

def update_amount_slashed(params, substep, state_history, previous_state, policy_input):
    return 'amount_slashed', policy_input['amount_slashed']

def update_whistleblower_rewards(params, substep, state_history, previous_state, policy_input):
    return 'whistleblower_rewards', policy_input['whistleblower_rewards']
