import model.constants as constants


def policy_calculate_yields(params, substep, state_history, previous_state):
    eth_price = previous_state['eth_price']
    eth_staked = previous_state['eth_staked']
    number_of_validators = previous_state['number_of_validators']
    validating_rewards = previous_state['validating_rewards']
    whistleblower_rewards = previous_state['whistleblower_rewards']
    validating_penalties = previous_state['validating_penalties']
    total_tips_to_validators = previous_state['total_tips_to_validators']
    total_costs = 0 # TODO implement validator costs

    rewards_for_online_validators = validating_rewards + whistleblower_rewards - validating_penalties + total_tips_to_validators
    
    total_revenue = number_of_validators * rewards_for_online_validators / constants.gwei * eth_price
    total_profit = total_revenue - total_costs
    revenue_yields = total_revenue * constants.epochs_per_year / eth_staked
    profit_yields = total_profit * constants.epochs_per_year / eth_staked

    return {
        'total_revenue': total_revenue,
        'total_profit': total_profit,
        'revenue_yields': revenue_yields,
        'profit_yields': profit_yields,
    }

def update_total_revenue(params, substep, state_history, previous_state, policy_input):
    return 'total_revenue', policy_input['total_revenue']

def update_total_profit(params, substep, state_history, previous_state, policy_input):
    return 'total_profit', policy_input['total_profit']

def update_revenue_yields(params, substep, state_history, previous_state, policy_input):
    return 'revenue_yields', policy_input['revenue_yields']

def update_profit_yields(params, substep, state_history, previous_state, policy_input):
    return 'profit_yields', policy_input['profit_yields']
