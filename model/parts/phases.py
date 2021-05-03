import datetime

import model.simulation_configuration as simulation
import model.constants as constants
from model.types import Phase


def policy_phases(params, substep, state_history, previous_state):
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

    # Initialize phase
    if current_phase == None:
        current_phase = phase
    else:
        current_phase = Phase(current_phase)

    # Transition through phases
    if phase == Phase.ALL:
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
        current_phase = Phase.PHASE_0
    elif phase == Phase.POST_EIP1559:
        current_phase = Phase.POST_EIP1559
    elif phase == Phase.POST_MERGE:
        current_phase = Phase.POST_MERGE
    else:
        raise Exception("Invalid Phase selected")

    return {
        "phase": current_phase.value,
        "timestamp": timestamp,
    }
