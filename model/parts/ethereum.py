import typing

import model.constants as constants
from model.types import ETH, USD_per_ETH, Gwei


"""
# Ethereum

* Basic policies and mechanisms shared between the Eth1 and Eth2 systems
"""


def policy_network_issuance(
    params, substep, state_history, previous_state
) -> typing.Dict[str, ETH]:
    # State Variables
    amount_slashed = previous_state["amount_slashed"]
    total_basefee = previous_state["total_basefee"]
    total_tips_to_validators = previous_state["total_tips_to_validators"]
    total_online_validator_rewards = previous_state["total_online_validator_rewards"]

    # Calculate network issuance in Gwei and ETH
    # total_online_validator_rewards includes tips to validators, which is not issuance, and is removed
    network_issuance = (
        (total_online_validator_rewards - total_tips_to_validators)
        - amount_slashed
        - total_basefee
    ) / constants.gwei

    return {
        "network_issuance": network_issuance,
    }


def policy_eip1559_transaction_pricing(
    params, substep, state_history, previous_state
) -> typing.Dict[str, Gwei]:
    """EIP1559 Transaction Pricing Mechanism
    A transaction pricing mechanism that includes fixed-per-block network fee
    that is burned and dynamically expands/contracts block sizes to deal with transient congestion.

    See https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1559.md
    """

    # Parameters
    dt = params["dt"]
    eip1559_avg_transactions_per_day = params["eip1559_avg_transactions_per_day"]
    eip1559_avg_gas_per_transaction = params["eip1559_avg_gas_per_transaction"]
    eip1559_basefee = params["eip1559_basefee"]
    eip1559_avg_tip_amount = params["eip1559_avg_tip_amount"]

    # Calculate total basefee and tips to validators
    total_transactions = eip1559_avg_transactions_per_day // constants.epochs_per_day
    total_gas_used = total_transactions * eip1559_avg_gas_per_transaction
    total_basefee = total_gas_used * eip1559_basefee
    total_tips_to_validators = total_gas_used * eip1559_avg_tip_amount

    return {
        "total_basefee": total_basefee * dt,
        "total_tips_to_validators": total_tips_to_validators * dt,
    }


def update_eth_price(
    params, substep, state_history, previous_state, policy_input
) -> (str, USD_per_ETH):
    # Parameters
    dt = params["dt"]
    eth_price_process = params["eth_price_process"]

    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]

    # Get the ETH price sample for the current run and timestep
    eth_price_sample = eth_price_process(run, timestep * dt)

    return "eth_price", eth_price_sample


def update_eth_supply(
    params, substep, state_history, previous_state, policy_input
) -> (str, ETH):
    # Policy Inputs
    network_issuance = policy_input["network_issuance"]

    # State variables
    eth_supply = previous_state["eth_supply"]

    return "eth_supply", eth_supply + network_issuance
