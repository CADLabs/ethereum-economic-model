import model.constants as constants


def policy_eip1559(params, substep, state_history, previous_state):
    '''EIP1559 Mechanism
    A transaction pricing mechanism that includes fixed-per-block network fee
    that is burned and dynamically expands/contracts block sizes to deal with transient congestion.

    See https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1559.md
    '''
    
    # Parameters
    eip1559_avg_transactions_per_day = params['eip1559_avg_transactions_per_day']
    eip1559_avg_gas_per_transaction = params['eip1559_avg_gas_per_transaction']
    eip1559_basefee = params['eip1559_basefee']
    eip1559_avg_tip_amount = params['eip1559_avg_tip_amount']

    # Calculate total basefee and tips to validators
    total_transactions = eip1559_avg_transactions_per_day // constants.epochs_per_day
    total_gas_used = (eip1559_avg_transactions_per_day * eip1559_avg_gas_per_transaction) / constants.epochs_per_day
    total_basefee = total_gas_used * eip1559_basefee
    total_tips_to_validators = total_gas_used * eip1559_avg_tip_amount

    return {
        'total_basefee': total_basefee,
        'total_tips_to_validators': total_tips_to_validators,
    }
