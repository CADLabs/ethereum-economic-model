"""
Misc. utility and helper functions
"""

import copy
from dataclasses import field
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
    """A generic State Update Function to update a State Variable directly from a Policy Signal

    Args:
        state_variable (str): State Variable key
        signal_key (str, optional): Policy Signal key. Defaults to None.

    Returns:
        Callable: A generic State Update Function
    """
    if not signal_key:
        signal_key = state_variable
    return partial(_update_from_signal, state_variable, signal_key)


def local_variables(_locals):
    return {
        key: _locals[key]
        for key in [_key for _key in _locals.keys() if "__" not in _key]
    }


def default(obj):
    return field(default_factory=lambda: copy.copy(obj))
