"""
# Proof of Stake Incentives

* Calculation of PoS attestation and block proposal rewards and penalties
* Calculation of PoS slashing penalties
"""

import math
import typing

import model.constants as constants
from model.types import Gwei
import model.parts.spec as spec


def policy_attestation_penalties(
    params, substep, state_history, previous_state
) -> typing.Dict[str, Gwei]:
    """
    Derived from: https://github.com/ethereum/eth2.0-specs/blob/dev/specs/altair/beacon-chain.md#get_flag_index_deltas

    Extract from spec:
    ```python
    penalties[index] += Gwei(base_reward * weight // WEIGHT_DENOMINATOR)
    ```
    """

    # Parameters
    TIMELY_SOURCE_WEIGHT = params["TIMELY_SOURCE_WEIGHT"]
    TIMELY_TARGET_WEIGHT = params["TIMELY_TARGET_WEIGHT"]
    TIMELY_HEAD_WEIGHT = params["TIMELY_HEAD_WEIGHT"]
    WEIGHT_DENOMINATOR = params["WEIGHT_DENOMINATOR"]

    # State Variables
    base_reward = previous_state["base_reward"]
    number_of_validators_offline = previous_state["number_of_validators_offline"]

    # Calculate validating penalties
    validating_penalties = (
        (TIMELY_SOURCE_WEIGHT + TIMELY_TARGET_WEIGHT + TIMELY_HEAD_WEIGHT)
        / WEIGHT_DENOMINATOR
        * base_reward
    )
    # Aggregation over all offline validators
    validating_penalties *= number_of_validators_offline

    return {"validating_penalties": validating_penalties}


def policy_attestation_rewards(
    params, substep, state_history, previous_state
) -> typing.Dict[str, Gwei]:
    """
    Derived from: https://github.com/ethereum/eth2.0-specs/blob/dev/specs/altair/beacon-chain.md#get_flag_index_deltas

    Extract from spec:
    ```python
    reward_numerator = base_reward * weight * unslashed_participating_increments
    rewards[index] += Gwei(reward_numerator // (active_increments * WEIGHT_DENOMINATOR))
    ```
    """

    # Parameters
    TIMELY_SOURCE_WEIGHT = params["TIMELY_SOURCE_WEIGHT"]
    TIMELY_TARGET_WEIGHT = params["TIMELY_TARGET_WEIGHT"]
    TIMELY_HEAD_WEIGHT = params["TIMELY_HEAD_WEIGHT"]
    WEIGHT_DENOMINATOR = params["WEIGHT_DENOMINATOR"]

    # State Variables
    base_reward = previous_state["base_reward"]
    number_of_validators = previous_state["number_of_validators"]
    number_of_validators_online = previous_state["number_of_validators_online"]

    # Calculate total source reward
    # All submitted attestations have to match source vote
    source_reward = (TIMELY_SOURCE_WEIGHT / WEIGHT_DENOMINATOR) * base_reward
    # Scale reward by the proportion of validators who also got the attestation in time and correctly
    source_reward *= number_of_validators_online / number_of_validators
    # Aggregation over all online validators; assumes one correct vote per online validator per epoch
    source_reward *= number_of_validators_online

    # Calculate total target reward
    target_reward = (TIMELY_TARGET_WEIGHT / WEIGHT_DENOMINATOR) * base_reward
    # Scale reward by the proportion of validators who also got the attestation in time and correctly
    target_reward *= number_of_validators_online / number_of_validators
    # Aggregation over all online validators; assumes one correct vote per online validator per epoch
    target_reward *= number_of_validators_online

    # Calculate total head reward
    head_reward = (TIMELY_HEAD_WEIGHT / WEIGHT_DENOMINATOR) * base_reward
    # Scale reward by the proportion of validators who also got the attestation in time and correctly
    head_reward *= number_of_validators_online / number_of_validators
    # Aggregation over all online validators; assumes one correct vote per online validator per epoch
    head_reward *= number_of_validators_online

    return {
        "source_reward": source_reward,
        "target_reward": target_reward,
        "head_reward": head_reward,
    }


def policy_sync_committee(
    params, substep, state_history, previous_state
) -> typing.Dict[str, Gwei]:
    """
    Derived from: https://github.com/ethereum/eth2.0-specs/blob/dev/specs/altair/beacon-chain.md#sync-committee-processing

    Extract from spec:
    ```python
    # Compute participant and proposer rewards
    total_active_increments = get_total_active_balance(state) // EFFECTIVE_BALANCE_INCREMENT
    total_base_rewards = Gwei(get_base_reward_per_increment(state) * total_active_increments)
    max_participant_rewards = Gwei(total_base_rewards * SYNC_REWARD_WEIGHT // WEIGHT_DENOMINATOR // SLOTS_PER_EPOCH)
    participant_reward = Gwei(max_participant_rewards // SYNC_COMMITTEE_SIZE)
    proposer_reward = Gwei(participant_reward * PROPOSER_WEIGHT // (WEIGHT_DENOMINATOR - PROPOSER_WEIGHT))
    ```
    """

    # Parameters
    SYNC_REWARD_WEIGHT = params["SYNC_REWARD_WEIGHT"]
    WEIGHT_DENOMINATOR = params["WEIGHT_DENOMINATOR"]

    # State Variables
    base_reward = previous_state["base_reward"]
    number_of_validators = previous_state["number_of_validators"]
    number_of_validators_online = previous_state["number_of_validators_online"]

    # Calculate total sync reward
    total_base_rewards = base_reward * number_of_validators_online
    sync_reward = total_base_rewards * SYNC_REWARD_WEIGHT // WEIGHT_DENOMINATOR
    # Scale reward by the percentage of online validators
    sync_reward *= number_of_validators_online / number_of_validators

    return {"sync_reward": sync_reward}


def policy_block_proposal(
    params, substep, state_history, previous_state
) -> typing.Dict[str, Gwei]:
    """
    Derived from: https://github.com/ethereum/eth2.0-specs/blob/dev/specs/altair/beacon-chain.md#modified-process_attestation

    Extract from spec:
    ```python
    # Participation flag indices
    participation_flag_indices = []
    if is_matching_head and is_matching_target and state.slot == data.slot + MIN_ATTESTATION_INCLUSION_DELAY:
        participation_flag_indices.append(TIMELY_HEAD_FLAG_INDEX)
    if is_matching_source and state.slot <= data.slot + integer_squareroot(SLOTS_PER_EPOCH):
        participation_flag_indices.append(TIMELY_SOURCE_FLAG_INDEX)
    if is_matching_target and state.slot <= data.slot + SLOTS_PER_EPOCH:
        participation_flag_indices.append(TIMELY_TARGET_FLAG_INDEX)

    # Update epoch participation flags
    proposer_reward_numerator = 0
    for index in get_attesting_indices(state, data, attestation.aggregation_bits):
        for flag_index, weight in get_flag_indices_and_weights():
            if flag_index in participation_flag_indices and not has_flag(epoch_participation[index], flag_index):
                epoch_participation[index] = add_flag(epoch_participation[index], flag_index)
                proposer_reward_numerator += get_base_reward(state, index) * weight

    # Reward proposer
    proposer_reward_denominator = (WEIGHT_DENOMINATOR - PROPOSER_WEIGHT) * WEIGHT_DENOMINATOR // PROPOSER_WEIGHT
    proposer_reward = Gwei(proposer_reward_numerator // proposer_reward_denominator)
    increase_balance(state, get_beacon_proposer_index(state), proposer_reward)
    ```
    """

    # Parameters
    WEIGHT_DENOMINATOR = params["WEIGHT_DENOMINATOR"]
    TIMELY_SOURCE_WEIGHT = params["TIMELY_SOURCE_WEIGHT"]
    TIMELY_TARGET_WEIGHT = params["TIMELY_TARGET_WEIGHT"]
    TIMELY_HEAD_WEIGHT = params["TIMELY_HEAD_WEIGHT"]
    PROPOSER_WEIGHT = params["PROPOSER_WEIGHT"]

    # State Variables
    base_reward = previous_state["base_reward"]
    sync_reward = previous_state["sync_reward"]
    number_of_validators_online = previous_state["number_of_validators_online"]
    number_of_validators = previous_state["number_of_validators"]

    # Calculate block proposer reward
    proposer_reward_numerator = base_reward * (
        TIMELY_SOURCE_WEIGHT + TIMELY_TARGET_WEIGHT + TIMELY_HEAD_WEIGHT
    )
    # Aggregate over all attestations in the epoch
    # Assumes every online validator gets one correct source, target, and head vote per epoch
    proposer_reward_numerator *= number_of_validators_online
    # Normalize by the sum of weights so that proposer rewards are 1/8th of base reward
    proposer_reward_denominator = (
        (WEIGHT_DENOMINATOR - PROPOSER_WEIGHT) * WEIGHT_DENOMINATOR // PROPOSER_WEIGHT
    )
    block_proposer_reward = Gwei(
        proposer_reward_numerator // proposer_reward_denominator
    )

    # Add block proposer reward for including sync committee attestations
    # See https://github.com/ethereum/eth2.0-specs/blob/dev/specs/altair/beacon-chain.md#sync-committee-processing
    block_proposer_reward += (
        sync_reward * PROPOSER_WEIGHT // (WEIGHT_DENOMINATOR - PROPOSER_WEIGHT)
    )

    return {"block_proposer_reward": block_proposer_reward}


def policy_slashing(
    params, substep, state_history, previous_state
) -> typing.Dict[str, Gwei]:
    # Parameters
    dt = params["dt"]
    slashing_events_per_1000_epochs = params["slashing_events_per_1000_epochs"]

    # Calculate total number of slashing events in current epoch
    number_of_slashing_events = slashing_events_per_1000_epochs / 1000

    # Calculate amount slashed, whistleblower reward, and proposer reward for a single slashing event
    amount_slashed, whistleblower_reward, proposer_reward = spec.slash_validator(
        params, previous_state
    )

    # Scale amount slashed and rewards by the number of slashing events per epoch
    amount_slashed *= number_of_slashing_events
    whistleblower_reward *= number_of_slashing_events
    proposer_reward *= number_of_slashing_events

    # The whistleblower and the block proposer who includes the slashing receive a reward
    whistleblower_rewards = whistleblower_reward + proposer_reward

    return {
        "amount_slashed": amount_slashed * dt,
        "whistleblower_rewards": whistleblower_rewards * dt,
    }


def update_base_reward(
    params, substep, state_history, previous_state, policy_input
) -> (str, Gwei):
    # Parameters
    dt = params["dt"]

    # Get base reward per validator
    base_reward_per_validator: Gwei = spec.get_base_reward(params, previous_state)

    # By scaling the base reward by our unit of time dt (in epochs),
    # we can scale all rewards and penalties by the same unit of time
    return "base_reward", Gwei(base_reward_per_validator) * dt


def update_validating_rewards(
    params, substep, state_history, previous_state, policy_input
) -> (str, Gwei):
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

    # Assert validating rewards should be less than equal to the maximum validating rewards
    max_validating_rewards = number_of_validators_online * base_reward
    assert validating_rewards <= max_validating_rewards

    return "validating_rewards", validating_rewards
