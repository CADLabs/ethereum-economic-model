import math

import model.constants as constants
from model.types import Gwei
from model.parameters import Parameters
from model.state_variables import StateVariables


"""
See:
* https://github.com/ethereum/eth2.0-specs/blob/dev/specs/altair/beacon-chain.md
"""


# Beacon state accessors


def get_total_active_balance(params: Parameters, state: StateVariables) -> Gwei:
    '''
    ```
    See https://github.com/ethereum/eth2.0-specs/blob/dev/specs/phase0/beacon-chain.md#get_total_active_balance

    def get_total_active_balance(state: BeaconState) -> Gwei:
        """
        Return the combined effective balance of the active validators.
        Note: ``get_total_balance`` returns ``EFFECTIVE_BALANCE_INCREMENT`` Gwei minimum to avoid divisions by zero.
        """
        return get_total_balance(state, set(get_active_validator_indices(state, get_current_epoch(state))))
    ```
    '''

    # Parameters
    EFFECTIVE_BALANCE_INCREMENT = params["EFFECTIVE_BALANCE_INCREMENT"]
    MAX_EFFECTIVE_BALANCE = params["MAX_EFFECTIVE_BALANCE"]

    # State Variables
    eth_staked = state["eth_staked"]
    number_of_validators = state["number_of_validators"]

    # Calculate total active balance
    total_active_balance = (
        eth_staked * constants.gwei
        - eth_staked * constants.gwei % EFFECTIVE_BALANCE_INCREMENT
    )
    max_total_active_balance = MAX_EFFECTIVE_BALANCE * number_of_validators

    total_active_balance = min(
        total_active_balance, max_total_active_balance
    )

    return Gwei(max(EFFECTIVE_BALANCE_INCREMENT, total_active_balance))


def get_base_reward_per_increment(params: Parameters, state: StateVariables) -> Gwei:
    EFFECTIVE_BALANCE_INCREMENT = params["EFFECTIVE_BALANCE_INCREMENT"]
    BASE_REWARD_FACTOR = params["BASE_REWARD_FACTOR"]

    return Gwei(
        EFFECTIVE_BALANCE_INCREMENT
        * BASE_REWARD_FACTOR
        // math.sqrt(get_total_active_balance(params, state))
    )


def get_base_reward(params: Parameters, state: StateVariables) -> Gwei:
    MAX_EFFECTIVE_BALANCE = params["MAX_EFFECTIVE_BALANCE"]
    EFFECTIVE_BALANCE_INCREMENT = params["EFFECTIVE_BALANCE_INCREMENT"]

    average_effective_balance = state["average_effective_balance"]

    increments = (
        min(average_effective_balance, MAX_EFFECTIVE_BALANCE)
        // EFFECTIVE_BALANCE_INCREMENT
    )

    return Gwei(increments * get_base_reward_per_increment(params, state))


def get_proposer_reward(params: Parameters, state: StateVariables) -> Gwei:
    PROPOSER_REWARD_QUOTIENT = params["PROPOSER_REWARD_QUOTIENT"]
    return Gwei(get_base_reward(params, state) // PROPOSER_REWARD_QUOTIENT)


# Beacon state mutators


def slash_validator(params: Parameters, state: StateVariables) -> (Gwei, Gwei, Gwei):
    MIN_SLASHING_PENALTY_QUOTIENT = params["MIN_SLASHING_PENALTY_QUOTIENT"]
    WHISTLEBLOWER_REWARD_QUOTIENT = params["WHISTLEBLOWER_REWARD_QUOTIENT"]
    PROPOSER_WEIGHT = params["PROPOSER_WEIGHT"]
    WEIGHT_DENOMINATOR = params["WEIGHT_DENOMINATOR"]

    average_effective_balance = state["average_effective_balance"]

    slashed = Gwei(average_effective_balance // MIN_SLASHING_PENALTY_QUOTIENT)
    whistleblower_reward = Gwei(
        average_effective_balance // WHISTLEBLOWER_REWARD_QUOTIENT
    )
    proposer_reward = Gwei(whistleblower_reward * PROPOSER_WEIGHT // WEIGHT_DENOMINATOR)

    return slashed, Gwei(whistleblower_reward - proposer_reward), proposer_reward


# Block processing

# def process_attestation(state: BeaconState, attestation: Attestation) -> None:
#     data = attestation.data
#     assert data.target.epoch in (get_previous_epoch(state), get_current_epoch(state))
#     assert data.target.epoch == compute_epoch_at_slot(data.slot)
#     assert data.slot + MIN_ATTESTATION_INCLUSION_DELAY <= state.slot <= data.slot + SLOTS_PER_EPOCH
#     assert data.index < get_committee_count_per_slot(state, data.target.epoch)

#     committee = get_beacon_committee(state, data.slot, data.index)
#     assert len(attestation.aggregation_bits) == len(committee)

#     if data.target.epoch == get_current_epoch(state):
#         epoch_participation = state.current_epoch_participation
#         justified_checkpoint = state.current_justified_checkpoint
#     else:
#         epoch_participation = state.previous_epoch_participation
#         justified_checkpoint = state.previous_justified_checkpoint

#     # Matching roots
#     is_matching_head = data.beacon_block_root == get_block_root_at_slot(state, data.slot)
#     is_matching_source = data.source == justified_checkpoint
#     is_matching_target = data.target.root == get_block_root(state, data.target.epoch)
#     assert is_matching_source

#     # Verify signature
#     assert is_valid_indexed_attestation(state, get_indexed_attestation(state, attestation))

#     # Participation flag indices
#     participation_flag_indices = []
#     if is_matching_head and is_matching_target and state.slot == data.slot + MIN_ATTESTATION_INCLUSION_DELAY:
#         participation_flag_indices.append(TIMELY_HEAD_FLAG_INDEX)
#     if is_matching_source and state.slot <= data.slot + integer_squareroot(SLOTS_PER_EPOCH):
#         participation_flag_indices.append(TIMELY_SOURCE_FLAG_INDEX)
#     if is_matching_target and state.slot <= data.slot + SLOTS_PER_EPOCH:
#         participation_flag_indices.append(TIMELY_TARGET_FLAG_INDEX)

#     # Update epoch participation flags
#     proposer_reward_numerator = 0
#     for index in get_attesting_indices(state, data, attestation.aggregation_bits):
#         for flag_index, weight in get_flag_indices_and_weights():
#             if flag_index in participation_flag_indices and not has_flag(epoch_participation[index], flag_index):
#                 epoch_participation[index] = add_flag(epoch_participation[index], flag_index)
#                 proposer_reward_numerator += get_base_reward(state, index) * weight

#     # Reward proposer
#     proposer_reward_denominator = (WEIGHT_DENOMINATOR - PROPOSER_WEIGHT) * WEIGHT_DENOMINATOR // PROPOSER_WEIGHT
#     proposer_reward = Gwei(proposer_reward_numerator // proposer_reward_denominator)
#     increase_balance(state, get_beacon_proposer_index(state), proposer_reward)

# def process_sync_committee(state: BeaconState, aggregate: SyncAggregate) -> None:
#     # Verify sync committee aggregate signature signing over the previous slot block root
#     committee_pubkeys = state.current_sync_committee.pubkeys
#     participant_pubkeys = [pubkey for pubkey, bit in zip(committee_pubkeys, aggregate.sync_committee_bits) if bit]
#     previous_slot = max(state.slot, Slot(1)) - Slot(1)
#     domain = get_domain(state, DOMAIN_SYNC_COMMITTEE, compute_epoch_at_slot(previous_slot))
#     signing_root = compute_signing_root(get_block_root_at_slot(state, previous_slot), domain)
#     assert eth2_fast_aggregate_verify(participant_pubkeys, signing_root, aggregate.sync_committee_signature)

#     # Compute participant and proposer rewards
#     total_active_increments = get_total_active_balance(state) // EFFECTIVE_BALANCE_INCREMENT
#     total_base_rewards = Gwei(get_base_reward_per_increment(state) * total_active_increments)
#     max_participant_rewards = Gwei(total_base_rewards * SYNC_REWARD_WEIGHT // WEIGHT_DENOMINATOR // SLOTS_PER_EPOCH)
#     participant_reward = Gwei(max_participant_rewards // SYNC_COMMITTEE_SIZE)
#     proposer_reward = Gwei(participant_reward * PROPOSER_WEIGHT // (WEIGHT_DENOMINATOR - PROPOSER_WEIGHT))

#     # Apply participant and proposer rewards
#     committee_indices = get_sync_committee_indices(state, get_current_epoch(state))
#     participant_indices = [index for index, bit in zip(committee_indices, aggregate.sync_committee_bits) if bit]
#     for participant_index in participant_indices:
#         increase_balance(state, participant_index, participant_reward)
#         increase_balance(state, get_beacon_proposer_index(state), proposer_reward)


# Epoch processing

# def process_rewards_and_penalties(state: BeaconState) -> None:
#     # No rewards are applied at the end of `GENESIS_EPOCH` because rewards are for work done in the previous epoch
#     if get_current_epoch(state) == GENESIS_EPOCH:
#         return

#     flag_indices_and_numerators = get_flag_indices_and_weights()
#     flag_deltas = [get_flag_index_deltas(state, index, numerator) for (index, numerator) in flag_indices_and_numerators]
#     deltas = flag_deltas + [get_inactivity_penalty_deltas(state)]
#     for (rewards, penalties) in deltas:
#         for index in range(len(state.validators)):
#             increase_balance(state, ValidatorIndex(index), rewards[index])
#             decrease_balance(state, ValidatorIndex(index), penalties[index])

# def process_slashings(state: BeaconState) -> None:
#     epoch = get_current_epoch(state)
#     total_balance = get_total_active_balance(state)
#     adjusted_total_slashing_balance = min(sum(state.slashings) * PROPORTIONAL_SLASHING_MULTIPLIER_ALTAIR, total_balance)
#     for index, validator in enumerate(state.validators):
#         if validator.slashed and epoch + EPOCHS_PER_SLASHINGS_VECTOR // 2 == validator.withdrawable_epoch:
#             increment = EFFECTIVE_BALANCE_INCREMENT  # Factored out from penalty numerator to avoid uint64 overflow
#             penalty_numerator = validator.effective_balance // increment * adjusted_total_slashing_balance
#             penalty = penalty_numerator // total_balance * increment
#             decrease_balance(state, ValidatorIndex(index), penalty)
