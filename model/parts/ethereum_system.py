"""
# Ethereum System

Policy Functions and State Update Functions shared between the Eth1 and Eth2 systems.
"""

import typing
import datetime

import model.constants as constants
from model import constants as constants
from model.types import ETH, USD_per_ETH, Gwei, Stage


def policy_upgrade_stages(params, substep, state_history, previous_state):
    """Upgrade Stages Policy
    Transitions the model from one stage in the Ethereum network
    upgrade process to the next at different milestones.

    This is essentially a finite-state machine: https://en.wikipedia.org/wiki/Finite-state_machine
    """

    # Parameters
    dt = params["dt"]
    stage: Stage = params["stage"]
    date_start = params["date_start"]
    date_eip1559 = params["date_eip1559"]
    date_pos = params["date_pos"]

    # State Variables
    current_stage = previous_state["stage"]
    timestep = previous_state["timestep"]

    # Calculate current timestamp from timestep
    timestamp = date_start + datetime.timedelta(
        days=(timestep * dt / constants.epochs_per_day)
    )

    # Initialize stage State Variable at start of simulation
    if current_stage == None:
        current_stage = stage
    else:
        # Convert Stage enum value (int) to Stage enum
        current_stage = Stage(current_stage)

    # Stage finite-state machine
    if stage == Stage.ALL:
        # If Stage ALL selected, transition through all stages
        # at different timestamps
        if (
            current_stage in [Stage.ALL, Stage.BEACON_CHAIN]
            and timestamp < date_eip1559
        ):
            current_stage = Stage.BEACON_CHAIN
        elif (
            current_stage in [Stage.BEACON_CHAIN, Stage.EIP1559]
            and timestamp < date_pos
        ):
            current_stage = Stage.EIP1559
        else:
            current_stage = Stage.PROOF_OF_STAKE
    elif stage == Stage.BEACON_CHAIN:
        # If Stage BEACON_CHAIN selected, only execute single stage
        current_stage = Stage.BEACON_CHAIN
    elif stage == Stage.EIP1559:
        # If Stage EIP1559 selected, only execute single stage
        current_stage = Stage.EIP1559
    elif stage == Stage.PROOF_OF_STAKE:
        # If Stage PROOF_OF_STAKE selected, only execute single stage
        current_stage = Stage.PROOF_OF_STAKE
    else:
        # Else, raise exception if invalid Stage
        raise Exception("Invalid Stage selected")

    return {
        "stage": current_stage.value,
        "timestamp": timestamp,
    }


def policy_network_issuance(
    params, substep, state_history, previous_state
) -> typing.Dict[str, ETH]:
    """Network Issuance Policy Function
    Calculate the total network issuance and issuance from Proof of Work block rewards.
    """

    # Parameters
    dt = params["dt"]
    daily_pow_issuance = params["daily_pow_issuance"]

    # State Variables
    stage = previous_state["stage"]
    amount_slashed = previous_state["amount_slashed"]
    total_basefee = previous_state["total_basefee"]
    total_tips_to_validators = previous_state["total_tips_to_validators"]
    total_online_validator_rewards = previous_state["total_online_validator_rewards"]

    # Calculate network issuance in ETH
    network_issuance = (
        # Remove tips to validators which is not issuance (ETH transferred rather than minted)
        (total_online_validator_rewards - total_tips_to_validators)
        - amount_slashed
        - total_basefee
    ) / constants.gwei

    # Calculate Proof of Work issuance
    pow_issuance = (
        daily_pow_issuance / constants.epochs_per_day
        if Stage(stage) in [Stage.BEACON_CHAIN, Stage.EIP1559]
        else 0
    )
    network_issuance += pow_issuance * dt

    return {
        "network_issuance": network_issuance,
        "pow_issuance": pow_issuance,
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

    stage = Stage(previous_state["stage"])
    if not stage in [Stage.EIP1559, Stage.PROOF_OF_STAKE]:
        return {
            "basefee": 0,
            "total_basefee": 0,
            "total_tips_to_miners": 0,
            "total_tips_to_validators": 0,
        }

    # Parameters
    dt = params["dt"]
    gas_target_process = params["gas_target_process"]  # Gas
    ELASTICITY_MULTIPLIER = params["ELASTICITY_MULTIPLIER"]
    BASE_FEE_MAX_CHANGE_DENOMINATOR = params["BASE_FEE_MAX_CHANGE_DENOMINATOR"]
    eip1559_basefee_process = params["eip1559_basefee_process"]
    eip1559_tip_process = params["eip1559_tip_process"]

    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]
    previous_basefee = previous_state["basefee"]

    # Get samples for current run and timestep from basefee, tip, and transaction processes
    basefee = eip1559_basefee_process(run, timestep * dt)  # Gwei per Gas

    gas_target = gas_target_process(run, timestep * dt)  # Gas

    # Ensure basefee changes by no more than 1 / BASE_FEE_MAX_CHANGE_DENOMINATOR %
    # assert (
    #     abs(basefee - previous_basefee) / previous_basefee
    #     <= constants.slots_per_epoch / BASE_FEE_MAX_CHANGE_DENOMINATOR
    #     if timestep > 1
    #     else True
    # ), "basefee changed by more than 1 / BASE_FEE_MAX_CHANGE_DENOMINATOR %"

    avg_tip_amount = eip1559_tip_process(run, timestep * dt)  # Gwei per Gas

    if stage in [Stage.EIP1559]:
        gas_used = constants.pow_blocks_per_epoch * gas_target  # Gas
    else:  # stage is Stage.PROOF_OF_STAKE
        gas_used = constants.slots_per_epoch * gas_target  # Gas

    # Calculate total basefee and tips to validators
    total_basefee = gas_used * basefee  # Gwei
    total_tips = gas_used * avg_tip_amount  # Gwei

    if stage in [Stage.PROOF_OF_STAKE]:
        total_tips_to_miners = 0
        total_tips_to_validators = total_tips
    else:
        total_tips_to_miners = total_tips
        total_tips_to_validators = 0

    # Check if the block used too much gas
    assert (
        gas_used <= gas_target * ELASTICITY_MULTIPLIER * constants.slots_per_epoch
    ), "invalid block: too much gas used"

    return {
        "basefee": basefee,
        "total_basefee": total_basefee * dt,
        "total_tips_to_miners": total_tips_to_miners * dt,
        "total_tips_to_validators": total_tips_to_validators * dt,
    }


def update_eth_price(
    params, substep, state_history, previous_state, policy_input
) -> typing.Tuple[str, USD_per_ETH]:
    """ETH Price State Update Function
    Update the ETH price from the `eth_price_process`.
    """

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
) -> typing.Tuple[str, ETH]:
    """ETH Supply State Update Function
    Update the ETH supply from the Network Issuance Policy Function.
    """

    # Policy Inputs
    network_issuance = policy_input["network_issuance"]

    # State variables
    eth_supply = previous_state["eth_supply"]

    return "eth_supply", eth_supply + network_issuance
