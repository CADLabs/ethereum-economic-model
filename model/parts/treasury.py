"""

Domain Treasury

"""

import typing

from model.types import POLYGN


# Added
# TODO: Need to add unlocking mechanism
def policy_domain_treasury_balance(
    params, substep, state_history, previous_state
) -> typing.Dict[str, POLYGN]:

    # Parameters

    # State Variables
    domain_treasury_balance = previous_state["domain_treasury_balance_locked"]
    public_base_fee_to_domain_treasury = previous_state["public_base_fee_to_domain_treasury"]
    private_base_fee_to_domain_treasury = previous_state["private_base_fee_to_domain_treasury"]
    
    domain_treasury_balance +=  public_base_fee_to_domain_treasury + private_base_fee_to_domain_treasury 

    return {
        "domain_treasury_balance_locked": domain_treasury_balance,
    }