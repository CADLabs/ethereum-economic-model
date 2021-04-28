"""
# Ethereum System

Policy Functions and State Update Functions shared between the Eth1 and Eth2 systems.
"""

import typing

import model.constants as constants
from model.types import ETH, USD_per_ETH, Gwei


def policy_network_issuance(
    params, substep, state_history, previous_state
) -> typing.Dict[str, ETH]:
    # State Variables
    amount_slashed = previous_state["amount_slashed"]
    total_basefee = previous_state["total_basefee"]
    total_tips_to_validators = previous_state["total_tips_to_validators"]
    total_online_validator_rewards = previous_state["total_online_validator_rewards"]

    # Calculate network issuance in ETH
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

    See:
    * https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1559.md
    * https://eips.ethereum.org/EIPS/eip-1559
    """

    # Parameters
    dt = params["dt"]
    gas_target = params["gas_target"] # Gas
    ELASTICITY_MULTIPLIER = params["ELASTICITY_MULTIPLIER"]
    eip1559_avg_basefee = params["eip1559_avg_basefee"] # Gwei per Gas
    eip1559_avg_tip_amount = params["eip1559_avg_tip_amount"] # Gwei per Gas
    
    # Calculate total basefee and tips to validators
    # Assume on average the gas used per block is equal to the gas target
    gas_used = gas_target
    total_basefee = gas_used * eip1559_avg_basefee # Gwei
    total_tips_to_validators = gas_used * eip1559_avg_tip_amount # Gwei

    # Check if the block used too much gas
    assert gas_used <= gas_target * ELASTICITY_MULTIPLIER, 'invalid block: too much gas used'

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
