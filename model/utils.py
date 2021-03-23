from functools import partial


def _update_from_signal(
    state_variable,
    signal_key,
    params,
    substep,
    state_history,
    previous_state,
    policy_input,
):
    return state_variable, policy_input[signal_key]


def update_from_signal(state_variable, signal_key=None):
    """
    A generic State Update Function to update a state variable directly from a policy signal
    """
    if not signal_key:
        signal_key = state_variable
    return partial(_update_from_signal, state_variable, signal_key)
