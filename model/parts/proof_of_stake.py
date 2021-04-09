import math
import model.constants as constants
from model.types import Gwei
import model.parts.spec as spec


"""
# Proof of Stake

* Calculation of PoS attestation and block proposal rewards and penalties
* Calculation of PoS slashing penalties
"""


def policy_attestation_penalties(params, substep, state_history, previous_state):
    # Parameters
    number_of_validating_penalties = params["number_of_validating_penalties"]

    # State Variables
    base_reward = previous_state["base_reward"]
    number_of_validators_offline = previous_state["number_of_validators_offline"]

    # Calculate validating penalties
    validating_penalties = (
        base_reward * number_of_validators_offline * number_of_validating_penalties
    )

    return {"validating_penalties": validating_penalties}


def policy_attestation_rewards(params, substep, state_history, previous_state):
    # Parameters
    TIMELY_SOURCE_WEIGHT = params["TIMELY_SOURCE_WEIGHT"]
    TIMELY_TARGET_WEIGHT = params["TIMELY_TARGET_WEIGHT"]
    TIMELY_HEAD_WEIGHT = params["TIMELY_HEAD_WEIGHT"]
    WEIGHT_DENOMINATOR = params["WEIGHT_DENOMINATOR"]

    # State Variables
    base_reward = previous_state["base_reward"]
    number_of_validators_online = previous_state["number_of_validators_online"]

    # Calculate source reward
    # All submitted attestations have to match source vote
    source_reward = (TIMELY_SOURCE_WEIGHT / WEIGHT_DENOMINATOR) * base_reward
    # Aggregation over all active validators
    source_reward *= number_of_validators_online

    # Calculate target reward
    target_reward = (TIMELY_TARGET_WEIGHT / WEIGHT_DENOMINATOR) * base_reward
    # Aggregation over all active validators
    target_reward *= number_of_validators_online

    # Calculate head reward
    head_reward = (TIMELY_HEAD_WEIGHT / WEIGHT_DENOMINATOR) * base_reward
    # Aggregation over all active validators
    head_reward *= number_of_validators_online

    return {
        "source_reward": source_reward,
        "target_reward": target_reward,
        "head_reward": head_reward,
    }


def policy_sync_committee(params, substep, state_history, previous_state):
    # Parameters
    SYNC_COMMITTEE_SIZE = params["SYNC_COMMITTEE_SIZE"]
    SLOTS_PER_EPOCH = params["SLOTS_PER_EPOCH"]
    SYNC_REWARD_WEIGHT = params["SYNC_REWARD_WEIGHT"]
    WEIGHT_DENOMINATOR = params["WEIGHT_DENOMINATOR"]

    # State Variables
    base_reward = previous_state["base_reward"]
    number_of_validators_online = previous_state["number_of_validators_online"]

    # Calculate aggregate sync reward
    sync_reward = (SYNC_REWARD_WEIGHT / WEIGHT_DENOMINATOR) * (1 / SLOTS_PER_EPOCH) * (1 / SYNC_COMMITTEE_SIZE) * base_reward
    # Aggregation over all committee members over all slots in one epoch
    sync_reward *= SYNC_COMMITTEE_SIZE * SLOTS_PER_EPOCH
    # Aggregation over all active validators
    sync_reward *= number_of_validators_online

    return {"sync_reward": sync_reward}


def policy_block_proposal(params, substep, state_history, previous_state):
    # Parameters
    PROPOSER_REWARD_QUOTIENT = params["PROPOSER_REWARD_QUOTIENT"]
    WEIGHT_DENOMINATOR = params["WEIGHT_DENOMINATOR"]
    TIMELY_SOURCE_WEIGHT = params["TIMELY_SOURCE_WEIGHT"]
    TIMELY_TARGET_WEIGHT = params["TIMELY_TARGET_WEIGHT"]
    TIMELY_HEAD_WEIGHT = params["TIMELY_HEAD_WEIGHT"]
    SYNC_REWARD_WEIGHT = params["SYNC_REWARD_WEIGHT"]

    # State Variables
    source_reward = previous_state["source_reward"]
    target_reward = previous_state["target_reward"]
    head_reward = previous_state["head_reward"]
    sync_reward = previous_state["sync_reward"]

    # Calculate block proposer reward
    block_proposer_reward = (1 / PROPOSER_REWARD_QUOTIENT) * (source_reward + target_reward + head_reward + sync_reward)
    # Normalize by the sum of weights so that proposer rewards are 1/8th of base reward
    block_proposer_reward *= (WEIGHT_DENOMINATOR / (TIMELY_SOURCE_WEIGHT + TIMELY_TARGET_WEIGHT + TIMELY_HEAD_WEIGHT + SYNC_REWARD_WEIGHT))
    
    return {"block_proposer_reward": block_proposer_reward}


def policy_slashing(params, substep, state_history, previous_state):
    # Parameters
    slashing_events_per_1000_epochs = params["slashing_events_per_1000_epochs"]

    # Calculate total number of slashing events in current epoch
    number_of_slashing_events = slashing_events_per_1000_epochs / 1000

    # Calculate amount slashed, whistleblower reward, and proposer reward for a single slashing event
    amount_slashed, whistleblower_reward, proposer_reward = spec.slash_validator(params, previous_state)

    # Scale slashed and rewards by the number of slashing events per epoch
    amount_slashed *= number_of_slashing_events
    whistleblower_reward *= number_of_slashing_events
    proposer_reward *= number_of_slashing_events

    return {
        "amount_slashed": amount_slashed,
        "whistleblower_rewards": whistleblower_reward + proposer_reward,
    }


def update_base_reward(params, substep, state_history, previous_state, policy_input) -> (str, Gwei):
    """Update Base Reward
    Calculate and update base reward state variable
    """

    # Get base reward per validator
    base_reward_per_validator: Gwei = spec.get_base_reward(params, previous_state)

    return "base_reward", Gwei(base_reward_per_validator)


def update_validating_rewards(
    params, substep, state_history, previous_state, policy_input
):
    # State Variables
    block_proposer_reward = previous_state["block_proposer_reward"]
    sync_reward = previous_state["sync_reward"]

    source_reward = previous_state["source_reward"]
    target_reward = previous_state["target_reward"]
    head_reward = previous_state["head_reward"]

    base_reward = previous_state["base_reward"]
    number_of_validators_online = previous_state["number_of_validators_online"]

    # Calculate total validating rewards
    validating_rewards = (
        block_proposer_reward
        + source_reward
        + target_reward
        + head_reward
        + sync_reward
    )

    # Check validating reward conditions
    total_reward = number_of_validators_online * base_reward
    assert sync_reward == (1 / 8) * total_reward
    assert block_proposer_reward == (1 / 8) * total_reward
    assert source_reward + target_reward + head_reward == (3 / 4) * total_reward
    assert validating_rewards <= total_reward

    return "validating_rewards", validating_rewards
