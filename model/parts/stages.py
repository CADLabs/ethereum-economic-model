"""Ethereum Upgrade Stages
The Stages module contains the logic for transitioning the model
from one stage in the Ethereum network upgrade process to the next at different milestones.
"""

import datetime

import model.constants as constants
from model.types import Stage


def policy_stages(params, substep, state_history, previous_state):
    """Stages Policy
    Transitions the model from one stage in the Ethereum network
    upgrade process to the next at different milestones.

    This is essentially a finite-state machine: https://en.wikipedia.org/wiki/Finite-state_machine
    """
    # Parameters
    dt = params["dt"]
    stage: Stage = params["stage"]
    date_start = params["date_start"]
    date_eip1559 = params["date_eip1559"]
    date_pos = params["date_pos"]

    # State Variables
    current_stage = previous_state["stage"]
    timestep = previous_state["timestep"]

    # Calculate current timestamp from timestep
    timestamp = date_start + datetime.timedelta(
        days=(timestep * dt / constants.epochs_per_day)
    )

    # Initialize stage State Variable at start of simulation
    if current_stage == None:
        current_stage = stage
    else:
        # Convert Stage enum value (int) to Stage enum
        current_stage = Stage(current_stage)

    # Stage finite-state machine
    if stage == Stage.ALL:
        # If Stage ALL selected, transition through all stages
        # at different timestamps
        if (
            current_stage in [Stage.ALL, Stage.BEACON_CHAIN]
            and timestamp < date_eip1559
        ):
            current_stage = Stage.BEACON_CHAIN
        elif (
            current_stage in [Stage.BEACON_CHAIN, Stage.EIP1559]
            and timestamp < date_pos
        ):
            current_stage = Stage.EIP1559
        else:
            current_stage = Stage.PROOF_OF_STAKE
    elif stage == Stage.BEACON_CHAIN:
        # If Stage BEACON_CHAIN selected, only execute single stage
        current_stage = Stage.BEACON_CHAIN
    elif stage == Stage.EIP1559:
        # If Stage EIP1559 selected, only execute single stage
        current_stage = Stage.EIP1559
    elif stage == Stage.PROOF_OF_STAKE:
        # If Stage PROOF_OF_STAKE selected, only execute single stage
        current_stage = Stage.PROOF_OF_STAKE
    else:
        # Else, raise exception if invalid Stage
        raise Exception("Invalid Stage selected")

    return {
        "stage": current_stage.value,
        "timestamp": timestamp,
    }
