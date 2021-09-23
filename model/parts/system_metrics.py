"""
# System Metrics

Calculation of metrics such as validator operational costs and yields.
"""

import typing

import model.constants as constants
from model.types import Percentage, Gwei

# @Ross
import numpy as np
from model.system_parameters import validator_environments  

def policy_validator_costs(
    params, substep, state_history, previous_state
) -> typing.Dict[str, any]:
    """
    ## Validator Costs Policy Function
    Calculate the aggregate validator costs.
    """
    # Parameters
    dt = params["dt"]

    # @Ross
    avg_pool_size = params["avg_pool_size"]
    if(avg_pool_size not None):
        validator_percentage_distribution = params["validator_percentage_distribution"]
    else:
        validator_percentage_distribution = previous_state["validator_percentage_distribution"]

    validator_hardware_costs_per_epoch = params["validator_hardware_costs_per_epoch"]
    validator_cloud_costs_per_epoch = params["validator_cloud_costs_per_epoch"]
    validator_third_party_costs_per_epoch = params[
        "validator_third_party_costs_per_epoch"
    ]

    # State Variables
    eth_price = previous_state["eth_price"]
    number_of_validators = previous_state["number_of_active_validators"]
    total_online_validator_rewards = previous_state["total_online_validator_rewards"]

    # Calculate hardware, cloud, and third-party costs per validator type
    validator_count_distribution = (
        number_of_validators * validator_percentage_distribution
    )

    validator_hardware_costs = (
        validator_count_distribution * validator_hardware_costs_per_epoch * dt
    )

    validator_cloud_costs = (
        validator_count_distribution * validator_cloud_costs_per_epoch * dt
    )

    validator_third_party_costs = (
        validator_percentage_distribution
        * validator_third_party_costs_per_epoch  # % of total
        * total_online_validator_rewards
    )
    validator_third_party_costs /= constants.gwei  # Convert from Gwei to ETH
    validator_third_party_costs *= eth_price  # Convert from ETH to Dollars

    # Calculate total validator costs per validator type and total network costs
    validator_costs = (
        validator_hardware_costs + validator_cloud_costs + validator_third_party_costs
    )
    total_network_costs = validator_costs.sum(axis=0)

    return {
        "validator_count_distribution": validator_count_distribution,
        "validator_hardware_costs": validator_hardware_costs,
        "validator_cloud_costs": validator_cloud_costs,
        "validator_third_party_costs": validator_third_party_costs,
        "validator_costs": validator_costs,
        "total_network_costs": total_network_costs,
    }


def policy_validator_yields(
    params, substep, state_history, previous_state
) -> typing.Dict[str, any]:
    """
    ## Validator Yields Policy Function
    Calculate the aggregate validator revenue and profit yields.
    """
    # Parameters
    dt = params["dt"]

    # @Ross
    avg_pool_size = params["avg_pool_size"]
    if(avg_pool_size not None):
        validator_percentage_distribution = params["validator_percentage_distribution"]
    else:
        validator_percentage_distribution = previous_state["validator_percentage_distribution"]


    # State Variables
    eth_price = previous_state["eth_price"]
    eth_staked = previous_state["eth_staked"]
    validator_costs = previous_state["validator_costs"]
    total_network_costs = previous_state["total_network_costs"]
    total_online_validator_rewards = previous_state["total_online_validator_rewards"]
    validator_count_distribution = previous_state["validator_count_distribution"]
    average_effective_balance = previous_state["average_effective_balance"]

    # Calculate ETH staked per validator type
    validator_eth_staked = validator_count_distribution * average_effective_balance
    validator_eth_staked /= constants.gwei  # Convert from Gwei to ETH

    # Calculate the revenue per validator type
    validator_revenue = (
        validator_percentage_distribution * total_online_validator_rewards
    )
   
    validator_revenue /= constants.gwei  # Convert from Gwei to ETH
    validator_revenue *= eth_price  # Convert from ETH to Dollars

    # Calculate the profit per validator type
    validator_profit = validator_revenue - validator_costs

    # Calculate the revenue yields per validator type
    validator_revenue_yields = validator_revenue / (validator_eth_staked * eth_price)
    validator_revenue_yields *= constants.epochs_per_year / dt  # Annualize value

    # Calculate the profit yields per validator type
    validator_profit_yields = validator_profit / (validator_eth_staked * eth_price)
    validator_profit_yields *= constants.epochs_per_year / dt  # Annualize value

    # Calculate the total network revenue
    total_revenue = validator_revenue.sum(axis=0)

    # Calculate the total network profit
    total_profit = total_revenue - total_network_costs

    # Calculate the total network revenue yields
    total_revenue_yields = total_revenue / (eth_staked * eth_price)
    total_revenue_yields *= constants.epochs_per_year / dt  # Annualize value

    # Calculate the total network profit yields
    total_profit_yields = total_profit / (eth_staked * eth_price)
    total_profit_yields *= constants.epochs_per_year / dt  # Annualize value

    return {
        # Per validator type
        "validator_eth_staked": validator_eth_staked,
        "validator_revenue": validator_revenue,
        "validator_profit": validator_profit,
        "validator_revenue_yields": validator_revenue_yields,
        "validator_profit_yields": validator_profit_yields,
        # Aggregate
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "total_revenue_yields": total_revenue_yields,
        "total_profit_yields": total_profit_yields,
    }





# @Ross
def policy_validator_pooled_returns(
    params, substep, state_history, previous_state
    ) -> typing.String[str, any]:
    """
    ## Validator Pooled Returns Policy Function
    Compounding mechanism to calculate new validator instances created by pooling returns in staking pools.
    """
    # Constants
    stake_requirement = constants.eth_deposited_per_validator

    # Parameters
    avg_pool_size = params["avg_pool_size"] # assert not > environment size?
    eth_price = previous_state["eth_price"]

    # State Variables
    validator_profit_USD = previous_state["validator_profit"] # array
    validator_pool_profits = previous_state["validator_pool_profits"] # array
    validator_count_distribution = previous_state["validator_count_distribution"] # array
    
    # Function variables
    number_of_validator_environments = len(validator_environments)
    new_shared_validators = np.zeros(len(number_of_validator_environments), dtype=int)
    pool_validator_indeces = [2, 3, 4] #update so we are not using hard-coded values
    total_pool_validators = 0 # init counter

    for i in pool_validator_indeces: 

        # Calculate total number of validators in pools
        total_pool_validators += validator_count_distribution[i]

        # disaggregrate profits to individual validator
        avg_individual_profit = (validator_profit[i] / eth_price) / validator_distribution_count[i] 
        new_pool_profit = avg_individual_profit * pool_size # in ETH

        # aggregrate any existing pool profits
        validator_pool_profits[i] += new_pool_profit

        # Calculate new shared validator instances
        new_shared_validators[i] = np.floor(validator_pool_profits[i] / stake_requirement)

        # Calculate remaining profit
        validator_pool_profits[i] -= new_shared_validators[i] * stake_requirement


    return {
        "validator_pool_profits": validator_pool_profits,
        "shared_validator_instances": new_shared_validators
    }








def policy_total_online_validator_rewards(
    params, substep, state_history, previous_state
) -> typing.Dict[str, Gwei]:
    """
    ## Total Online Validator Rewards Policy Function
    Calculate the aggregate total online validator rewards.
    """
    # State Variables
    validating_rewards = previous_state["validating_rewards"]
    validating_penalties = previous_state["validating_penalties"]
    whistleblower_rewards = previous_state["whistleblower_rewards"]
    total_priority_fee_to_validators = previous_state[
        "total_priority_fee_to_validators"
    ]
    total_realized_mev_to_validators = previous_state[
        "total_realized_mev_to_validators"
    ]

    # Calculate total rewards for online validators
    total_online_validator_rewards = (
        validating_rewards
        - validating_penalties
        + whistleblower_rewards
        + total_priority_fee_to_validators
        + total_realized_mev_to_validators * constants.gwei
    )

    return {"total_online_validator_rewards": total_online_validator_rewards}


def update_supply_inflation(
    params, substep, state_history, previous_state, policy_input
) -> typing.Tuple[str, Percentage]:
    """
    ## Supply Inflation State Update Function
    Update the annualized ETH supply inflation.
    """
    # Policy Inputs
    network_issuance = policy_input["network_issuance"]

    # Parameters
    dt = params["dt"]

    # State Variables
    eth_supply = previous_state["eth_supply"]

    # Calculate the ETH supply inflation
    supply_inflation = network_issuance / eth_supply
    supply_inflation *= constants.epochs_per_year / dt  # Annualize value

    return "supply_inflation", supply_inflation
