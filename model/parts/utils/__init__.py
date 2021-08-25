"""
Misc. utility and helper functions
"""

from model.state_variables import StateVariables
from model.system_parameters import Parameters


def get_number_of_awake_validators(params: Parameters, state: StateVariables) -> int:
    """
    Utility function used to return the number of awake validators.
    If the MAX_VALIDATOR_COUNT is disabled (set to None), it will return the number of active validators.
    """
    # Parameters
    MAX_VALIDATOR_COUNT = params["MAX_VALIDATOR_COUNT"]

    # State Variables
    if MAX_VALIDATOR_COUNT:
        number_of_validators = state["number_of_awake_validators"]
    else:
        number_of_validators = state["number_of_active_validators"]

    return number_of_validators
