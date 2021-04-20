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
    number_of_validators = previous_state["number_of_validators"]
    average_effective_balance = previous_state["average_effective_balance"]

    # If the eth_staked_process is defined
    if not eth_staked_process(0, 0) == None:
        # Get the ETH staked sample for the current run and timestep
        eth_staked = eth_staked_process(run, timestep * dt)
    # Else, calculate from the number of validators
    else:
        eth_staked = number_of_validators * average_effective_balance / constants.gwei

    # Assert expected conditions
    assert eth_staked <= eth_supply, f"{eth_staked=} can't be more than {eth_supply=}"

    return {"eth_staked": eth_staked}


def policy_validators(params, substep, state_history, previous_state):
    # Parameters
    dt = params["dt"]
    eth_staked_process = params["eth_staked_process"]
    validator_process = params["validator_process"]
    validator_internet_uptime = params["validator_internet_uptime"]
    validator_power_uptime = params["validator_power_uptime"]
    validator_technical_uptime = params["validator_technical_uptime"]

    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]
    eth_staked = previous_state["eth_staked"]
    number_of_validators = previous_state["number_of_validators"]
    number_of_validators_in_activation_queue = previous_state["number_of_validators_in_activation_queue"]
    average_effective_balance = previous_state["average_effective_balance"]

    # Calculate the net validators uptime
    validators_uptime = (
        validator_internet_uptime * validator_power_uptime * validator_technical_uptime
    )

    # Calculate the number of validators using ETH staked
    if number_of_validators == 0 or not eth_staked_process(0, 0) == None:
        number_of_validators = int(
            round(eth_staked / (average_effective_balance / constants.gwei))
        )
    else:
        new_validators_per_epoch = validator_process(run, timestep * dt)
        number_of_validators_in_activation_queue += new_validators_per_epoch * dt

        validator_churn_limit = spec.get_validator_churn_limit(params, previous_state) * dt
        activated_validators = len(
            range(number_of_validators_in_activation_queue)[
                :validator_churn_limit
            ]
        )

        number_of_validators += activated_validators
        number_of_validators_in_activation_queue -= activated_validators

    # Calculate the number of validators online and offline using validators uptime
    number_of_validators_online = int(round(number_of_validators * validators_uptime))
    number_of_validators_offline = number_of_validators - number_of_validators_online

    # Assert expected conditions
    assert (
        number_of_validators
        == number_of_validators_online + number_of_validators_offline
    )

    return {
        "number_of_validators_in_activation_queue": number_of_validators_in_activation_queue,
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
