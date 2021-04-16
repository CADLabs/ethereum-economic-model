import numpy as np
from pytest import approx

import model.constants as constants
import model.parts.spec as spec


"""
# Validators

* Implementation of the validator staking process
* Implementation of the new, online, and offline validator processes
* Calculation of the validator average effective balance
"""


def policy_staking(params, substep, state_history, previous_state):
    # Parameters
    dt = params["dt"]
    eth_staked_process = params["eth_staked_process"]

    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]
    eth_supply = previous_state["eth_supply"]

    # Get the ETH staked sample for the current run and timestep
    eth_staked = eth_staked_process(run, timestep * dt)

    assert eth_staked <= eth_supply, "ETH staked can't be more than ETH supply"

    return {"eth_staked": eth_staked}


def policy_validators(params, substep, state_history, previous_state):
    # Parameters
    validator_internet_uptime = params["validator_internet_uptime"]
    validator_power_uptime = params["validator_power_uptime"]
    validator_technical_uptime = params["validator_technical_uptime"]

    # State Variables
    eth_staked = previous_state["eth_staked"]
    average_effective_balance = previous_state["average_effective_balance"]

    # Calculate the net validators uptime
    validators_uptime = (
        validator_internet_uptime * validator_power_uptime * validator_technical_uptime
    )

    # Calculate the number of validators using ETH staked
    number_of_validators = int(
        round(eth_staked / (average_effective_balance / constants.gwei))
    )

    # Calculate the number of validators online and offline using validators uptime
    number_of_validators_online = int(round(number_of_validators * validators_uptime))
    number_of_validators_offline = number_of_validators - number_of_validators_online

    # Assert expected conditions are valid
    assert (
        number_of_validators
        == number_of_validators_online + number_of_validators_offline
    )

    return {
        "number_of_validators": number_of_validators,
        "number_of_validators_online": number_of_validators_online,
        "number_of_validators_offline": number_of_validators_offline,
    }


def policy_average_effective_balance(params, substep, state_history, previous_state):
    # State Variables
    number_of_validators = previous_state["number_of_validators"]

    # Get total active balance
    total_active_balance = spec.get_total_active_balance(params, previous_state)
    # Aggregate by averaging over all validators
    average_effective_balance = total_active_balance / number_of_validators

    return {"average_effective_balance": average_effective_balance}
