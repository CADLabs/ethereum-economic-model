"""
# Proof of Stake Incentives

Calculation of PoS incentives such as attestation and block proposal rewards and penalties.
"""

import typing

import model.parts.utils.ethereum_spec as spec
from model.parts.utils import get_number_of_awake_validators
from model.types import Gwei


def policy_attestation_rewards(
    params, substep, state_history, previous_state
) -> typing.Dict[str, Gwei]:
    """
    ## Attestation Rewards Policy Function
    Derived from https://github.com/ethereum/eth2.0-specs/blob/dev/specs/altair/beacon-chain.md#get_flag_index_deltas

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
    number_of_validators = get_number_of_awake_validators(params, previous_state)
    number_of_validators_online = (
        number_of_validators * previous_state["validator_uptime"]
    )

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


def policy_attestation_penalties(
    params, substep, state_history, previous_state
) -> typing.Dict[str, Gwei]:
    """
    ## Attestation Penalties Policy Function
    Validators are penalized for not attesting to the source, target, and head.

    Derived from https://github.com/ethereum/eth2.0-specs/blob/dev/specs/altair/beacon-chain.md#get_flag_index_deltas

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
    number_of_validators = get_number_of_awake_validators(params, previous_state)
    number_of_validators_offline = number_of_validators * (
        1 - previous_state["validator_uptime"]
    )

    # Calculate attestation penalties
    attestation_penalties = (
        (TIMELY_SOURCE_WEIGHT + TIMELY_TARGET_WEIGHT + TIMELY_HEAD_WEIGHT)
        / WEIGHT_DENOMINATOR
        * base_reward
    )
    # Aggregation over all offline validators
    attestation_penalties *= number_of_validators_offline

    return {"attestation_penalties": attestation_penalties}


def policy_sync_committee_reward(
    params, substep, state_history, previous_state
) -> typing.Dict[str, Gwei]:
    """
    ## Sync Committee Reward Policy Function
    Derived from https://github.com/ethereum/eth2.0-specs/blob/dev/specs/altair/beacon-chain.md#sync-aggregate-processing

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
    number_of_validators = get_number_of_awake_validators(params, previous_state)
    number_of_validators_online = (
        number_of_validators * previous_state["validator_uptime"]
    )

    # Calculate total base rewards
    total_base_rewards = base_reward * number_of_validators
    # Set sync reward to proportion of total base rewards
    sync_reward = total_base_rewards * SYNC_REWARD_WEIGHT // WEIGHT_DENOMINATOR
    # Scale reward by the percentage of online validators
    sync_reward *= number_of_validators_online / number_of_validators

    return {"sync_reward": sync_reward}


def policy_sync_committee_penalties(
    params, substep, state_history, previous_state
) -> typing.Dict[str, Gwei]:
    """
    ## Sync Committee Penalty Policy Function
    Derived from https://github.com/ethereum/eth2.0-specs/blob/dev/specs/altair/beacon-chain.md#sync-aggregate-processing

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
    number_of_validators = get_number_of_awake_validators(params, previous_state)
    number_of_validators_offline = number_of_validators * (
        1 - previous_state["validator_uptime"]
    )

    # Calculate total base rewards
    total_base_rewards = base_reward * number_of_validators
    # Set sync penalty to proportion of total base rewards
    sync_penalty = total_base_rewards * SYNC_REWARD_WEIGHT // WEIGHT_DENOMINATOR
    # Scale penalty by the percentage of offline validators
    sync_penalty *= number_of_validators_offline / number_of_validators

    return {"sync_committee_penalties": sync_penalty}


def policy_block_proposal_reward(
    params, substep, state_history, previous_state
) -> typing.Dict[str, Gwei]:
    """
    ## Block Proposal Reward Policy Function
    Derived from https://github.com/ethereum/eth2.0-specs/blob/dev/specs/altair/beacon-chain.md#modified-process_attestation

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
    number_of_validators = get_number_of_awake_validators(params, previous_state)
    number_of_validators_online = (
        number_of_validators * previous_state["validator_uptime"]
    )

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
    """
    ## Slashing Policy Function
    Derived from https://github.com/ethereum/eth2.0-specs/blob/dev/specs/altair/beacon-chain.md#modified-slash_validator

    Extract from spec:
    ```python
    state.slashings[epoch % EPOCHS_PER_SLASHINGS_VECTOR] += validator.effective_balance
    decrease_balance(state, slashed_index, validator.effective_balance // MIN_SLASHING_PENALTY_QUOTIENT_ALTAIR)

    # Apply proposer and whistleblower rewards
    proposer_index = get_beacon_proposer_index(state)
    if whistleblower_index is None:
        whistleblower_index = proposer_index
    whistleblower_reward = Gwei(validator.effective_balance // WHISTLEBLOWER_REWARD_QUOTIENT)
    proposer_reward = Gwei(whistleblower_reward * PROPOSER_WEIGHT // WEIGHT_DENOMINATOR)
    increase_balance(state, proposer_index, proposer_reward)
    increase_balance(state, whistleblower_index, Gwei(whistleblower_reward - proposer_reward))
    ```

    Derived from https://github.com/ethereum/eth2.0-specs/blob/dev/specs/altair/beacon-chain.md#slashings

    Extract from spec:
    ```python
    def process_slashings(state: BeaconState) -> None:
        epoch = get_current_epoch(state)
        total_balance = get_total_active_balance(state)
        adjusted_total_slashing_balance = min(sum(state.slashings) * PROPORTIONAL_SLASHING_MULTIPLIER_ALTAIR, total_balance)
        for index, validator in enumerate(state.validators):
            if validator.slashed and epoch + EPOCHS_PER_SLASHINGS_VECTOR // 2 == validator.withdrawable_epoch:
                increment = EFFECTIVE_BALANCE_INCREMENT  # Factored out from penalty numerator to avoid uint64 overflow
                penalty_numerator = validator.effective_balance // increment * adjusted_total_slashing_balance
                penalty = penalty_numerator // total_balance * increment
                decrease_balance(state, ValidatorIndex(index), penalty)
    ```
    """
    # Parameters
    dt = params["dt"]
    slashing_events_per_1000_epochs = params["slashing_events_per_1000_epochs"]
    MIN_SLASHING_PENALTY_QUOTIENT = params["MIN_SLASHING_PENALTY_QUOTIENT"]
    PROPORTIONAL_SLASHING_MULTIPLIER = params["PROPORTIONAL_SLASHING_MULTIPLIER"]
    EFFECTIVE_BALANCE_INCREMENT = params["EFFECTIVE_BALANCE_INCREMENT"]
    WHISTLEBLOWER_REWARD_QUOTIENT = params["WHISTLEBLOWER_REWARD_QUOTIENT"]
    PROPOSER_WEIGHT = params["PROPOSER_WEIGHT"]
    WEIGHT_DENOMINATOR = params["WEIGHT_DENOMINATOR"]

    # State Variables
    average_effective_balance = previous_state["average_effective_balance"]

    # Calculate slashing, whistleblower, and proposer reward for a single slashing event
    slashing = Gwei(average_effective_balance // MIN_SLASHING_PENALTY_QUOTIENT)
    whistleblower_reward = Gwei(
        average_effective_balance // WHISTLEBLOWER_REWARD_QUOTIENT
    )
    proposer_reward = Gwei(whistleblower_reward * PROPOSER_WEIGHT // WEIGHT_DENOMINATOR)
    whistleblower_reward = Gwei(whistleblower_reward - proposer_reward)

    # Calculate number of slashing events for current epoch
    number_of_slashing_events = slashing_events_per_1000_epochs / 1000

    # Calculate the individual penalty proportional to total slashings
    # in current time period using `PROPORTIONAL_SLASHING_MULTIPLIER`
    total_balance = spec.get_total_active_balance(params, previous_state)
    adjusted_total_slashing_balance = min(
        slashing * number_of_slashing_events * PROPORTIONAL_SLASHING_MULTIPLIER,
        total_balance,
    )
    increment = EFFECTIVE_BALANCE_INCREMENT
    penalty_numerator = (
        average_effective_balance // increment * adjusted_total_slashing_balance
    )
    proportional_penalty = penalty_numerator // total_balance * increment

    # Scale penalty by the number of slashing events per epoch
    amount_slashed = (slashing + proportional_penalty) * number_of_slashing_events
    # Scale rewards by the number of slashing events per epoch
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
) -> typing.Tuple[str, Gwei]:
    """
    ## Base Reward State Update Function
    Calculate and update base reward per validator
    """
    # Parameters
    dt = params["dt"]

    # Get base reward per validator
    base_reward_per_validator: Gwei = spec.get_base_reward(params, previous_state)

    # By scaling the base reward by our unit of time dt (in epochs),
    # we can scale all rewards and penalties by the same unit of time
    return "base_reward", Gwei(base_reward_per_validator) * dt


def update_validating_rewards(
    params, substep, state_history, previous_state, policy_input
) -> typing.Tuple[str, Gwei]:
    """
    ## Validating Rewards State Update Function
    Calculate and update total validating rewards

    i.e. rewards received for block proposal, attesting, and being a member of sync committee
    """
    # State Variables
    block_proposer_reward = previous_state["block_proposer_reward"]
    sync_reward = previous_state["sync_reward"]

    source_reward = previous_state["source_reward"]
    target_reward = previous_state["target_reward"]
    head_reward = previous_state["head_reward"]

    base_reward = previous_state["base_reward"]
    number_of_validators = get_number_of_awake_validators(params, previous_state)
    number_of_validators_online = (
        number_of_validators * previous_state["validator_uptime"]
    )

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


def update_validating_penalties(
    params, substep, state_history, previous_state, policy_input
) -> typing.Tuple[str, Gwei]:
    """
    ## Validating Penalties State Update Function
    Calculate and update total validating penalties

    i.e. penalties received for failing to attest, or failing to perform sync committee duties
    """
    # State Variables
    attestation_penalties = previous_state["attestation_penalties"]
    sync_committee_penalties = previous_state["sync_committee_penalties"]

    # Calculate total validating penalties
    validating_penalties = attestation_penalties + sync_committee_penalties

    return "validating_penalties", validating_penalties
