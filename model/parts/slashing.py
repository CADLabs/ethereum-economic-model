def policy_slashing(params, substep, state_history, previous_state):
    # Parameters
    whistleblower_reward_quotient = params['WHISTLEBLOWER_REWARD_QUOTIENT']
    min_slashing_penalty_quotient = params['MIN_SLASHING_PENALTY_QUOTIENT']
    slashing_events_per_1000_epochs = params['slashing_events_per_1000_epochs']

    # State Variables
    average_effective_balance = previous_state['average_effective_balance']

    # Calculate total number of slashing events in current epoch
    number_of_slashing_events = slashing_events_per_1000_epochs / 1000

    # Calculate amount slashed and whistleblower rewards for current epoch
    amount_slashed = number_of_slashing_events * average_effective_balance / min_slashing_penalty_quotient    
    whistleblower_rewards = average_effective_balance / whistleblower_reward_quotient * number_of_slashing_events

    return {
        'amount_slashed': amount_slashed,
        'whistleblower_rewards': whistleblower_rewards,
    }
