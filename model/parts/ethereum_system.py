"""
# Ethereum System

General Ethereum mechanisms, such as managing the system upgrade process,
the EIP-1559 transaction pricing mechanism, and updating the ETH price and ETH supply.
"""

import typing
import datetime
import numpy as np

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
    date_start = params["date_start"]

    # State Variables
    timestep = previous_state["timestep"]

    # Calculate current timestamp from timestep
    timestamp = date_start + datetime.timedelta(
        days=(timestep * dt / constants.epochs_per_day)
    )


    return {
        "timestamp": timestamp,
    }


# Edited
def policy_network_issuance(
    params, substep, state_history, previous_state
) -> typing.Dict[str, ETH]:
    """
    ## Network Issuance Policy Function

    Calculate the total network issuance and issuance from Proof of Work block rewards.
    """


    # State Variables
    amount_slashed = previous_state["amount_slashed"]
    inflation_rewards = previous_state["total_inflation_to_validators"]

    # Calculate network issuance in ETH
    network_issuance = (
        inflation_rewards
        - amount_slashed
    ) / constants.gwei


    return {
        "network_issuance": network_issuance,
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


# Edited
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

    # Parameters
    dt = params["dt"]
    gas_target_process = params["gas_target_process"]  # Gas
    ELASTICITY_MULTIPLIER = params["ELASTICITY_MULTIPLIER"]
    base_fee_process = params["base_fee_process"]
    priority_fee_process = params["priority_fee_process"]
    public_chain_treasury_extraction_rate = params["BASE_FEE_PUBLIC_QUOTIENT"]
    private_chain_treasury_extraction_rate = params["BASE_FEE_PRIVATE_QUOTIENTT"]

    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]
    public_chain_number = previous_state["PUBLIC_CHAINS_CNT"]
    private_chain_number = previous_state["PRIVATE_CHAINS_CNT"]
    private_treasury_balance = previous_state["private_treasury_balance"]


    total_chain_number = public_chain_number + private_chain_number

    # Get samples for current run and timestep from base fee, priority fee, and transaction processes
    base_fee_per_gas = base_fee_process(run, timestep * dt)  # Gwei per Gas

    gas_target = gas_target_process(run, timestep * dt)  # Gas

    avg_priority_fee_per_gas = priority_fee_process(run, timestep * dt)  # Gwei per Gas


    gas_used = constants.slots_per_epoch * gas_target  # Gas

    # Calculate the total base fee and priority fee for a single chain
    total_base_fee = gas_used * base_fee_per_gas  # Gwei
    total_priority_fee = gas_used * avg_priority_fee_per_gas  # Gwei


    # Calculate the fee sent to treasuries
    public_base_fee_to_domain_treasury = total_base_fee * public_chain_treasury_extraction_rate * public_chain_number
    private_base_fee_to_domain_treasury = total_base_fee * private_chain_treasury_extraction_rate * private_chain_number

    # Calculate the total priority fee to validators from all public and private chains
    total_priority_fee_to_validators = total_priority_fee * total_chain_number

    # Calculate the remain base fee to private chain owned treasury
    private_base_fee_to_private_treasury = np.repeat(
        total_base_fee * (1 - private_chain_treasury_extraction_rate), private_chain_number
    )


    # Check if the block used too much gas
    assert (
        gas_used <= gas_target * ELASTICITY_MULTIPLIER * constants.slots_per_epoch
    ), "invalid block: too much gas used"

    return {
        "public_base_fee_to_domain_treasury": public_base_fee_to_domain_treasury * dt,
        "private_base_fee_to_domain_treasury": private_base_fee_to_domain_treasury * dt,
        "total_priority_fee_to_validators": total_priority_fee_to_validators * dt,
        "private_treasury_balance": private_treasury_balance + private_base_fee_to_private_treasury * dt,
    }

# Added
def policy_inflation(params, substep, state_history, previous_state) -> typing.Dict[str, ETH]:
    """
    ## Inflation Policy

    Inflation is allocated to validators post Proof-of-Stake,
    using the `inflationary_rate_per_year` System Parameter.
    """
    
    # Parameters
    dt = params["dt"]
    inflationary_rate_per_year = params["inflationary_rate_per_year"]
    
    # State Variables
    polygn_supply = previous_state["polygn_supply"]

    total_inflation_to_validators = (
                polygn_supply * inflationary_rate_per_year / constants.epochs_per_year * dt
    )

    
    return {
        "total_inflation_to_validators": total_inflation_to_validators,
    }

# Edited
def update_polygn_price(
    params, substep, state_history, previous_state, policy_input
) -> typing.Tuple[str, USD_per_ETH]:
    """
    ## ETH Price State Update Function

    Update the ETH price from the `eth_price_process`.
    """

    # Parameters
    dt = params["dt"]
    polygn_price_process = params["polygn_price_process"]

    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]

    # Get the ETH price sample for the current run and timestep
    polygn_price_sample = polygn_price_process(run, timestep * dt)

    return "polygn_price", polygn_price_sample


# Edited
def update_polygn_supply(
    params, substep, state_history, previous_state, policy_input
) -> typing.Tuple[str, ETH]:
    """
    ## ETH Supply State Update Function

    Update the ETH supply from the Network Issuance Policy Function.
    """

    # Policy Inputs
    network_issuance = policy_input["network_issuance"]

    # State variables
    polygn_supply = previous_state["polygn_supply"]

    return "polygn_supply", polygn_supply + network_issuance
