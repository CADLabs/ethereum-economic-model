"""
# Validator Mechanisms

Validator processes such as validator activation, staking, and uptime.
"""

import typing
import numpy as np

import model.constants as constants
import model.parts.utils.ethereum_spec as spec
from model.parts.utils import get_number_of_awake_validators
from model.types import ETH, Gwei
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

    return {
        "eth_staked": eth_staked
    }


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
    avg_pool_size = params["avg_pool_size"]
    validator_process_percentage_distribution = params["validator_percentage_distribution"]

    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]
    number_of_active_validators = previous_state["number_of_active_validators"]
    number_of_validators_in_activation_queue = previous_state["number_of_validators_in_activation_queue"]
    average_effective_balance = previous_state["average_effective_balance"]
    validator_count_distribution = previous_state["validator_count_distribution"]
    validator_percentage_distribution = previous_state["validator_percentage_distribution"]
    shared_validator_instances = previous_state["shared_validator_instances"] 
    validators_in_activation_queue = previous_state["validators_in_activation_queue"]   


    # Calculate the number of validators using ETH staked
    if eth_staked_process(0, 0) is not None:
        eth_staked = eth_staked_process(run, timestep * dt)
        number_of_active_validators = int(
            round(eth_staked / (average_effective_balance / constants.gwei))
        )
        validator_count_distribution = (
                number_of_active_validators * validator_percentage_distribution
        )

    else:
        
        # Calculate the number of validators using the validator process
        if(avg_pool_size == None or avg_pool_size < 1): # returns true if analysis is not investigating compounding yields (see model extension #5) 
            new_validators_per_epoch = validator_process(run, timestep * dt)
            number_of_validators_in_activation_queue += new_validators_per_epoch * dt

            validator_churn_limit = (
                spec.get_validator_churn_limit(params, previous_state) * dt
            )
            activated_validators = min(
                number_of_validators_in_activation_queue, validator_churn_limit
            )

            number_of_active_validators += activated_validators
            number_of_validators_in_activation_queue -= activated_validators
        
            validator_count_distribution = (
                number_of_active_validators * validator_percentage_distribution
            )


        else:
            # Calculate the number of new validators from both validator-process and 
            # the pool compounding mechanism (model extention #5):

            # Update validator queue:
            validators_from_validator_process = validator_process(run, timestep * dt) * dt
            validators_from_validator_process_per_environment = np.round(validator_process_percentage_distribution * validators_from_validator_process).astype(int)
            new_validators_distribution = validators_from_validator_process_per_environment + shared_validator_instances
            
            validators_in_activation_queue += new_validators_distribution
            number_of_validators_in_activation_queue = validators_in_activation_queue.sum(axis=0)
            
            # Calculate churn limit and update active validator count:
            validator_churn_limit = (
                spec.get_validator_churn_limit(params, previous_state) * dt
            )
            activated_validators = min(
                (number_of_validators_in_activation_queue), validator_churn_limit
            )
            number_of_active_validators += activated_validators 


            # Allocate validators accordingly:
            new_validators_distribution_pct = ( # Calculate distribution percentage for new validators
                new_validators_distribution / new_validators_distribution.sum(axis=0)
            )
            # Allocate new validators to respective validator environments 
            validator_count_distribution +=  (
                new_validators_distribution_pct * activated_validators
            ).astype(int)
            # Calculate percentage distribution
            validator_percentage_distribution = (
                validator_count_distribution / number_of_active_validators
            )
            # Update the validator activation queue 
            validators_in_activation_queue -= np.round(new_validators_distribution_pct * activated_validators).astype(int)
            

            
            


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
        "validators_in_activation_queue": validators_in_activation_queue,
        "number_of_active_validators": number_of_active_validators,
        "number_of_awake_validators": number_of_awake_validators,
        "validator_uptime": validator_uptime,
        "validator_percentage_distribution": validator_percentage_distribution,
        "validator_count_distribution": validator_count_distribution,
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


