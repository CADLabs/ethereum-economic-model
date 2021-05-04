"""Ethereum Upgrade Phases
The Phases module contains the logic for transitioning the model
from one phase in the Ethereum network upgrade process to the next at different milestones.
"""

import datetime

import model.simulation_configuration as simulation
import model.constants as constants
from model.types import Phase


def policy_phases(params, substep, state_history, previous_state):
    """Phases Policy
    Transitions the model from one phase in the Ethereum network
    upgrade process to the next at different milestones.

    This is essentially a finite-state machine: https://en.wikipedia.org/wiki/Finite-state_machine
    """
    # Parameters
    dt = params["dt"]
    phase: Phase = params["phase"]
    date_start = params["date_start"]
    date_eip1559 = params["date_eip1559"]
    date_merge = params["date_merge"]

    # State Variables
    current_phase = previous_state["phase"]
    timestep = previous_state["timestep"]

    # Calculate current timestamp from timestep
    timestamp = date_start + datetime.timedelta(
        days=(timestep * dt / constants.epochs_per_day)
    )

    # Initialize phase State Variable at start of simulation
    if current_phase == None:
        current_phase = phase
    else:
        # Convert Phase enum value (int) to Phase enum
        current_phase = Phase(current_phase)

    # Phase finite-state machine
    if phase == Phase.ALL:
        # If Phase ALL selected, transition through all phases
        # at different timestamps
        if current_phase in [Phase.ALL, Phase.PHASE_0] and timestamp < date_eip1559:
            current_phase = Phase.PHASE_0
        elif (
            current_phase in [Phase.PHASE_0, Phase.POST_EIP1559]
            and timestamp < date_merge
        ):
            current_phase = Phase.POST_EIP1559
        else:
            current_phase = Phase.POST_MERGE
    elif phase == Phase.PHASE_0:
        # If Phase PHASE_0 selected, only execute single phase
        current_phase = Phase.PHASE_0
    elif phase == Phase.POST_EIP1559:
        # If Phase POST_EIP1559 selected, only execute single phase
        current_phase = Phase.POST_EIP1559
    elif phase == Phase.POST_MERGE:
        # If Phase POST_MERGE selected, only execute single phase
        current_phase = Phase.POST_MERGE
    else:
        # Else, raise exception if invalid Phase
        raise Exception("Invalid Phase selected")

    return {
        "phase": current_phase.value,
        "timestamp": timestamp,
    }
