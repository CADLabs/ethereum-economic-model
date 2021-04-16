import model.parts.spec as spec


def test_base_reward(params, substep, state_history, previous_state):
    EFFECTIVE_BALANCE_INCREMENT = params["EFFECTIVE_BALANCE_INCREMENT"]
    number_of_validators = previous_state["number_of_validators"]

    total_active_increments = spec.get_total_active_balance(params, previous_state) // EFFECTIVE_BALANCE_INCREMENT
    assert spec.get_base_reward(params, previous_state) * number_of_validators == spec.get_base_reward_per_increment(params, previous_state) * total_active_increments
    
    return
