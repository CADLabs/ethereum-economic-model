"""
# Ethereum System

General Ethereum mechanisms, such as managing the system upgrade process,
the EIP-1559 transaction pricing mechanism, and updating the ETH price and ETH supply.
"""

import typing
import datetime

from model import constants as constants
from model.types import ETH, USD_per_ETH, Gwei, Stage


def policy_upgrade_stages(params, substep, state_history, previous_state):
    """
    ## Upgrade Stages Policy

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
    if current_stage is None:
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
            current_stage in [Stage.ALL, Stage.BEACON_CHAIN, Stage.EIP1559]
            and timestamp < date_pos
        ):
            current_stage = Stage.EIP1559
        else:
            current_stage = Stage.PROOF_OF_STAKE
    elif stage == Stage.BEACON_CHAIN:
        # If Stage BEACON_CHAIN selected, only execute single stage
        current_stage = Stage.BEACON_CHAIN
    elif stage == Stage.EIP1559:
        # If Stage EIP-1559 selected, only execute single stage
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
    """
    ## Network Issuance Policy Function

    Calculate the total network issuance and issuance from Proof of Work block rewards.
    """

    # Parameters
    dt = params["dt"]
    daily_pow_issuance = params["daily_pow_issuance"]

    # State Variables
    stage = previous_state["stage"]
    amount_slashed = previous_state["amount_slashed"]
    total_base_fee = previous_state["total_base_fee"]
    total_priority_fee_to_validators = previous_state[
        "total_priority_fee_to_validators"
    ]
    total_online_validator_rewards = previous_state["total_online_validator_rewards"]

    # Calculate network issuance in ETH
    network_issuance = (
        # Remove priority fee to validators which is not issuance (ETH transferred rather than minted)
        (total_online_validator_rewards - total_priority_fee_to_validators)
        - amount_slashed
        - total_base_fee
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


def policy_mev(params, substep, state_history, previous_state) -> typing.Dict[str, ETH]:
    """
    ## Maximum Extractable Value (MEV) Policy

    MEV is allocated to miners pre Proof-of-Stake and validators post Proof-of-Stake,
    using the `mev_per_block` System Parameter.

    By default `mev_per_block` is set zero, to only consider the
    influence of Proof-of-Stake (PoS) incentives on validator yields.

    See [ASSUMPTIONS.md](ASSUMPTIONS.md) document for further details.
    """
    # Parameters
    dt = params["dt"]
    mev_per_block = params["mev_per_block"]

    # State Variables
    stage = Stage(previous_state["stage"])

    if stage in [Stage.PROOF_OF_STAKE]:
        total_realized_mev_to_miners = 0
        # Allocate realized MEV to validators post Proof-of-Stake
        total_realized_mev_to_validators = (
            mev_per_block * constants.slots_per_epoch * dt
        )
    else:  # Stage is pre Proof-of-Stake
        # Allocate realized MEV to miners pre Proof-of-Stake
        total_realized_mev_to_miners = (
            mev_per_block * constants.pow_blocks_per_epoch * dt
        )
        total_realized_mev_to_validators = 0

    return {
        "total_realized_mev_to_miners": total_realized_mev_to_miners,
        "total_realized_mev_to_validators": total_realized_mev_to_validators,
    }


def policy_eip1559_transaction_pricing(
    params, substep, state_history, previous_state
) -> typing.Dict[str, Gwei]:
    """
    ## EIP-1559 Transaction Pricing Policy

    A transaction pricing mechanism that includes fixed-per-block network fee
    that is burned and dynamically expands/contracts block sizes to deal with transient congestion.

    See:
    * https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1559.md
    * https://eips.ethereum.org/EIPS/eip-1559
    """

    stage = Stage(previous_state["stage"])
    if stage not in [Stage.EIP1559, Stage.PROOF_OF_STAKE]:
        return {
            "base_fee_per_gas": 0,
            "total_base_fee": 0,
            "total_priority_fee_to_miners": 0,
            "total_priority_fee_to_validators": 0,
        }

    # Parameters
    dt = params["dt"]
    gas_target_process = params["gas_target_process"]  # Gas
    ELASTICITY_MULTIPLIER = params["ELASTICITY_MULTIPLIER"]
    base_fee_process = params["base_fee_process"]
    priority_fee_process = params["priority_fee_process"]

    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]

    # Get samples for current run and timestep from base fee, priority fee, and transaction processes
    base_fee_per_gas = base_fee_process(run, timestep * dt)  # Gwei per Gas

    gas_target = gas_target_process(run, timestep * dt)  # Gas

    # Ensure basefee changes by no more than 1 / BASE_FEE_MAX_CHANGE_DENOMINATOR %
    _BASE_FEE_MAX_CHANGE_DENOMINATOR = params["BASE_FEE_MAX_CHANGE_DENOMINATOR"]
    # assert (
    #     abs(basefee - previous_basefee) / previous_basefee
    #     <= constants.slots_per_epoch / BASE_FEE_MAX_CHANGE_DENOMINATOR
    #     if timestep > 1
    #     else True
    # ), "basefee changed by more than 1 / BASE_FEE_MAX_CHANGE_DENOMINATOR %"

    avg_priority_fee_per_gas = priority_fee_process(run, timestep * dt)  # Gwei per Gas

    if stage in [Stage.EIP1559]:
        gas_used = constants.pow_blocks_per_epoch * gas_target  # Gas
    else:  # stage is Stage.PROOF_OF_STAKE
        gas_used = constants.slots_per_epoch * gas_target  # Gas

    # Calculate the total base fee and priority fee
    total_base_fee = gas_used * base_fee_per_gas  # Gwei
    total_priority_fee = gas_used * avg_priority_fee_per_gas  # Gwei

    if stage in [Stage.PROOF_OF_STAKE]:
        total_priority_fee_to_miners = 0
        total_priority_fee_to_validators = total_priority_fee
    else:
        total_priority_fee_to_miners = total_priority_fee
        total_priority_fee_to_validators = 0

    # Check if the block used too much gas
    assert (
        gas_used <= gas_target * ELASTICITY_MULTIPLIER * constants.slots_per_epoch
    ), "invalid block: too much gas used"

    return {
        "base_fee_per_gas": base_fee_per_gas,
        "total_base_fee": total_base_fee * dt,
        "total_priority_fee_to_miners": total_priority_fee_to_miners * dt,
        "total_priority_fee_to_validators": total_priority_fee_to_validators * dt,
    }


def update_eth_price(
    params, substep, state_history, previous_state, policy_input
) -> typing.Tuple[str, USD_per_ETH]:
    """
    ## ETH Price State Update Function

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
    """
    ## ETH Supply State Update Function

    Update the ETH supply from the Network Issuance Policy Function.
    """

    # Policy Inputs
    network_issuance = policy_input["network_issuance"]

    # State variables
    eth_supply = previous_state["eth_supply"]

    return "eth_supply", eth_supply + network_issuance
