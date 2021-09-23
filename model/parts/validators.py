"""
# Validator Mechanisms

Validator processes such as validator activation, staking, and uptime.
"""

import typing

import model.constants as constants
import model.parts.utils.ethereum_spec as spec
from model.parts.utils import get_number_of_awake_validators
from model.types import ETH, Gwei

# @Ross
import numpy as np
from model.system_parameters import validator_environments  


def policy_staking(
    params, substep, state_history, previous_state
) -> typing.Dict[str, ETH]:
    """
    ## Staking Policy
    A policy used when driving the model with the `eth_staked_process`,
    for generating phase-space analyses, e.g. simulating a set of discrete `eth_staked` values.

    When the `eth_staked_process` is disabled, the model is driven using the `validator_process`,
    for generating state-space analyses.
    """
    # Parameters
    dt = params["dt"]
    eth_staked_process = params["eth_staked_process"]

    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]
    eth_supply = previous_state["eth_supply"]
    number_of_validators = previous_state["number_of_active_validators"]
    average_effective_balance = previous_state["average_effective_balance"]

    # If the eth_staked_process is defined
    if eth_staked_process(0, 0) is not None:
        # Get the ETH staked sample for the current run and timestep
        eth_staked = eth_staked_process(run, timestep * dt)

    # Else, calculate from the number of validators
    else:
        eth_staked = number_of_validators * average_effective_balance / constants.gwei

    # Assert expected conditions
    assert eth_staked <= eth_supply, f"ETH staked can't be more than ETH supply"

    return {"eth_staked": eth_staked}


def policy_validators(params, substep, state_history, previous_state):
    """
    ## Validator Policy Function
    Calculate the number of validators driven by the ETH staked or validator processes.
    """
    # Parameters
    dt = params["dt"]
    eth_staked_process = params["eth_staked_process"]
    validator_process = params["validator_process"]
    validator_uptime_process = params["validator_uptime_process"]
    # @Ross
    avg_pool_size = params["avg_pool_size"]

    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]
    number_of_active_validators = previous_state["number_of_active_validators"]
    number_of_validators_in_activation_queue = previous_state[
        "number_of_validators_in_activation_queue"
    ]
    average_effective_balance = previous_state["average_effective_balance"]

    # @Ross
    number_of_validator_environments = len(validator_environments)
    # State Variables
    shared_validator_instances = previous_state["shared_validator_instances"]
    validator_count_distribution = previous_state["validator_count_distribution"] # array

    number_of_shared_validator_instances = shared_validator_instances.sum(axis=0)
    validator_percentage_distribution = previous_state["validator_percentage_distribution"]

    

    # Calculate the number of validators using ETH staked
    if eth_staked_process(0, 0) is not None:
        eth_staked = eth_staked_process(run, timestep * dt)
        number_of_active_validators = int(
            round(eth_staked / (average_effective_balance / constants.gwei))
        )

        # @Ross
        # Account for 'validator_pool_profits' in this process
    else:
        new_validators_per_epoch = validator_process(run, timestep * dt)
        number_of_validators_in_activation_queue += new_validators_per_epoch * dt

        validator_churn_limit = (
                spec.get_validator_churn_limit(params, previous_state) * dt
            )

        # @Ross
        # If simulating with pool compounding (model extension #5), this code block combines and allocates both the new validators from validator_process and from 
        # the shared validator instances from pools, and renormalizes the percentage distribution.
        if(avg_pool_size is not None and number_of_shared_validator_instances > 0):


            max_activated_validators = min(
                (number_of_validators_in_activation_queue + number_of_shared_validator_instances), validator_churn_limit
            )
            
            # Calculate what fraction of new validators are from the validator_process & compound pooling respectively:
            max_new_validators = number_of_validators_in_activation_queue + number_of_shared_validator_instances
            validator_process_fraction = number_of_validators_in_activation_queue /  max_new_validators
            shared_validator_instances_fraction = number_of_shared_validator_instances / max_new_validators

            # From above, determine where new validators will be allocated
            pool_validator_indeces = [2, 3, 4] #update so we are not using hard-coded values
            total_new_active_validators = 0

            for i in range(number_of_validator_environments):
                new_active_validators = int(max_activated_validators * validator_process_fraction * validator_percentage_distribution[i]) 
                validator_count_distribution[i] += new_active_validators 

                if(i in pool_validator_indeces): # add the shared validator instances
                    pool_environment_fraction = shared_validator_instances[i] / number_of_shared_validator_instances 
                    new_active_pool_validators = int(max_activated_validators * shared_validator_instances_fraction * pool_environment_fraction)
                    validator_count_distribution[i] += new_active_pool_validators


            number_of_active_validators += max_activated_validators
            number_of_validators_in_activation_queue -= max_activated_validators

            # Renormalize the distribution
            for i in range(number_of_validator_environments):
                validator_percentage_distribution[i] = validator_count_distribution[i] / number_of_active_validators

        else:

        
            activated_validators = min(
                number_of_validators_in_activation_queue, validator_churn_limit
            )

            number_of_active_validators += activated_validators
            number_of_validators_in_activation_queue -= activated_validators


    # Calculate the number of "awake" validators
    # See proposal: https://ethresear.ch/t/simplified-active-validator-cap-and-rotation-proposal
    number_of_awake_validators = spec.get_awake_validator_indices(
        params, previous_state
    )

    # Calculate the validator uptime
    validator_uptime = validator_uptime_process(run, timestep * dt)

    # Assume a participation of more than 2/3 due to lack of inactivity leak mechanism
    assert validator_uptime >= 2 / 3, "Validator uptime must be greater than 2/3"

    return {
        "number_of_validators_in_activation_queue": number_of_validators_in_activation_queue,
        "number_of_active_validators": number_of_active_validators,
        "number_of_awake_validators": number_of_awake_validators,
        "validator_uptime": validator_uptime,
        # @Ross
        "validator_percentage_distribution": validator_percentage_distribution,
        "validator_count_distribution": validator_count_distribution
    }


def policy_average_effective_balance(
    params, substep, state_history, previous_state
) -> typing.Dict[str, Gwei]:
    """
    ## Average Effective Balance Policy Function
    Calculate the validator average effective balance.
    """
    # State Variables
    number_of_validators = get_number_of_awake_validators(params, previous_state)

    # Get total active balance
    total_active_balance = spec.get_total_active_balance(params, previous_state)
    # Aggregate by averaging over all validators
    average_effective_balance = total_active_balance / number_of_validators

    return {"average_effective_balance": average_effective_balance}
