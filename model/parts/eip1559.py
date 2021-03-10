import model.constants as constants


def policy_eip1559(params, substep, state_history, previous_state):
    eip1559_avg_transactions_per_day = params['eip1559_avg_transactions_per_day']
    eip1559_avg_gas_per_transaction = params['eip1559_avg_gas_per_transaction']
    eip1559_basefee = params['eip1559_basefee']
    eip1559_avg_tip_amount = params['eip1559_avg_tip_amount']

    total_transactions = eip1559_avg_transactions_per_day // constants.epochs_per_day
    total_gas_used = (eip1559_avg_transactions_per_day * eip1559_avg_gas_per_transaction) / constants.epochs_per_day
    total_basefee = total_gas_used * eip1559_basefee
    total_tips_to_validators = total_gas_used * eip1559_avg_tip_amount

    return {
        'total_basefee': total_basefee,
        'total_tips_to_validators': total_tips_to_validators,
    }

def update_total_basefee(params, substep, state_history, previous_state, policy_input):
    return 'total_basefee', policy_input['total_basefee']

def update_total_tips_to_validators(params, substep, state_history, previous_state, policy_input):
    return 'total_tips_to_validators', policy_input['total_tips_to_validators']
