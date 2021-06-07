"""Ethereum Upgrade Stages
The Stages module contains the logic for transitioning the model
from one stage in the Ethereum network upgrade process to the next at different milestones.
"""

import datetime

import model.simulation_configuration as simulation
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
    date_merge = params["date_merge"]

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
        if current_stage in [Stage.ALL, Stage.PHASE_0] and timestamp < date_eip1559:
            current_stage = Stage.PHASE_0
        elif (
            current_stage in [Stage.PHASE_0, Stage.POST_EIP1559]
            and timestamp < date_merge
        ):
            current_stage = Stage.POST_EIP1559
        else:
            current_stage = Stage.POST_MERGE
    elif stage == Stage.PHASE_0:
        # If Stage PHASE_0 selected, only execute single stage
        current_stage = Stage.PHASE_0
    elif stage == Stage.POST_EIP1559:
        # If Stage POST_EIP1559 selected, only execute single stage
        current_stage = Stage.POST_EIP1559
    elif stage == Stage.POST_MERGE:
        # If Stage POST_MERGE selected, only execute single stage
        current_stage = Stage.POST_MERGE
    else:
        # Else, raise exception if invalid Stage
        raise Exception("Invalid Stage selected")

    return {
        "stage": current_stage.value,
        "timestamp": timestamp,
    }
