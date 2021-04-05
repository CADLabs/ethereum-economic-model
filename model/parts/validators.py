import numpy as np
from pytest import approx

import model.constants as constants


"""
# Validators

* Implementation of the validator staking process
* Implementation of the new, online, and offline validator processes
* Calculation of the validator average effective balance
"""


def policy_staking(params, substep, state_history, previous_state):
    # Parameters
    eth_staked_process = params["eth_staked_process"]

    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]
    eth_staked = previous_state["eth_staked"]

    # Get the staked ETH sample for the current run and timestep
    staked_eth = eth_staked_process(run, timestep) - eth_staked

    return {"staked_eth": staked_eth}


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
    # Parameters
    effective_balance_increment = params["EFFECTIVE_BALANCE_INCREMENT"]
    max_effective_balance = params["MAX_EFFECTIVE_BALANCE"]

    # State Variables
    eth_staked = previous_state["eth_staked"]
    number_of_validators = previous_state["number_of_validators"]

    # TODO check balance == eth_staked at aggregate
    # TODO confirm effective balance multiplied by both online and offline validators
    total_effective_balance = (
        eth_staked * constants.gwei
        - eth_staked * constants.gwei % effective_balance_increment
    )
    max_total_effective_balance = max_effective_balance * number_of_validators

    average_effective_balance = min(
        total_effective_balance, max_total_effective_balance
    )
    average_effective_balance /= number_of_validators

    return {"average_effective_balance": average_effective_balance}


def update_eth_staked(params, substep, state_history, previous_state, policy_input):
    eth_supply = previous_state["eth_supply"]
    eth_staked = previous_state["eth_staked"]
    staked_eth = policy_input["staked_eth"]

    assert (
        eth_staked + staked_eth <= eth_supply
    ), "ETH staked can't be more than ETH supply"

    return "eth_staked", eth_staked + staked_eth
