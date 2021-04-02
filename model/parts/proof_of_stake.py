import math
import model.constants as constants


'''
# Proof of Stake

* Calculation of PoS attestation and block proposal rewards and penalties
* Calculation of PoS slashing penalties
'''


def policy_penalties(params, substep, state_history, previous_state):
    # Parameters
    number_of_validating_penalties = params["number_of_validating_penalties"]

    # State Variables
    base_reward = previous_state["base_reward"]
    number_of_validators_offline = previous_state["number_of_validators_offline"]

    # Calculate validating penalties
    validating_penalties = (
        base_reward
        * number_of_validators_offline
        * number_of_validating_penalties
    )

    return {"validating_penalties": validating_penalties}


def policy_casper_ffg_vote(params, substep, state_history, previous_state):
    # State Variables
    base_reward = previous_state["base_reward"]
    number_of_validators = previous_state["number_of_validators"]
    number_of_validators_offline = previous_state["number_of_validators_offline"]

    validators_offline_pct = (
        number_of_validators_offline / number_of_validators
    )

    # Calculate source and target reward
    source_reward = (1 - validators_offline_pct) * base_reward * number_of_validators
    target_reward = source_reward

    return {
        "source_reward": source_reward,
        "target_reward": target_reward,
    }


def approximate_inclusion_distance(number_of_validators, validators_offline_pct):
    """Approximate Inclusion Distance
    See derivation: https://github.com/hermanjunge/eth2-reward-simulation/blob/master/assumptions.md#attester-incentives
    """
    if validators_offline_pct == 0:
        return 1
    
    inclusion_distance_denominator = 1 - validators_offline_pct
    inclusion_distance_denominator *= (
        math.log(1 - validators_offline_pct)
        / ((1 - validators_offline_pct) - 1)
        * number_of_validators
    )
    return 1 / inclusion_distance_denominator


def policy_lmd_ghost_vote(params, substep, state_history, previous_state):
    # Parameters
    proposer_reward_quotient = params["PROPOSER_REWARD_QUOTIENT"]

    # State Variables
    base_reward = previous_state["base_reward"]
    number_of_validators = previous_state["number_of_validators"]
    number_of_validators_offline = previous_state["number_of_validators_offline"]

    validators_offline_pct = (
        number_of_validators_offline / number_of_validators
    )

    head_reward = (1 - validators_offline_pct) * base_reward * number_of_validators

    # Inclusion delay reward
    inclusion_distance = approximate_inclusion_distance(
        number_of_validators, validators_offline_pct
    )
    block_attester_reward = (
        (1 - 1 / proposer_reward_quotient) * base_reward * (1 / inclusion_distance)
    )

    return {
        "head_reward": head_reward,
        "block_attester_reward": block_attester_reward,
    }


def policy_block_proposal(params, substep, state_history, previous_state):
    # Parameters
    proposer_reward_quotient = params["PROPOSER_REWARD_QUOTIENT"]

    # State Variables
    base_reward = previous_state["base_reward"]
    number_of_validators = previous_state["number_of_validators"]
    number_of_validators_offline = previous_state["number_of_validators_offline"]

    validators_offline_pct = (
        number_of_validators_offline / number_of_validators
    )

    inclusion_distance = approximate_inclusion_distance(
        number_of_validators, validators_offline_pct
    )
    block_proposer_reward = (
        (1 / proposer_reward_quotient) * base_reward * (1 / inclusion_distance)
    )

    return {"block_proposer_reward": block_proposer_reward}


def policy_slashing(params, substep, state_history, previous_state):
    # Parameters
    whistleblower_reward_quotient = params["WHISTLEBLOWER_REWARD_QUOTIENT"]
    min_slashing_penalty_quotient = params["MIN_SLASHING_PENALTY_QUOTIENT"]
    slashing_events_per_1000_epochs = params["slashing_events_per_1000_epochs"]

    # State Variables
    average_effective_balance = previous_state["average_effective_balance"]

    # Calculate total number of slashing events in current epoch
    number_of_slashing_events = slashing_events_per_1000_epochs / 1000

    # Calculate amount slashed and whistleblower rewards for current epoch
    amount_slashed = (
        average_effective_balance
        / min_slashing_penalty_quotient
        * number_of_slashing_events
    )
    whistleblower_rewards = (
        average_effective_balance
        / whistleblower_reward_quotient
        * number_of_slashing_events
    )

    return {
        "amount_slashed": amount_slashed,
        "whistleblower_rewards": whistleblower_rewards,
    }


def update_base_reward(params, substep, state_history, previous_state, policy_input):
    """Update Base Reward
    Calculate and update base reward state variable
    """

    # Parameters
    max_effective_balance = params["MAX_EFFECTIVE_BALANCE"]
    base_reward_factor = params["BASE_REWARD_FACTOR"]
    base_rewards_per_epoch = params["BASE_REWARDS_PER_EPOCH"]

    # State Variables
    eth_staked = previous_state["eth_staked"]

    # Policy Signals
    average_effective_balance = policy_input["average_effective_balance"]

    # Calculate base reward
    base_reward_per_validator = (
        (min(average_effective_balance, max_effective_balance) * base_reward_factor)
        // math.sqrt(eth_staked * constants.gwei)
        // base_rewards_per_epoch
    )

    return "base_reward", base_reward_per_validator


def update_validating_rewards(
    params, substep, state_history, previous_state, policy_input
):
    # Policy Signals
    block_proposer_reward = policy_input["block_proposer_reward"]
    block_attester_reward = policy_input["block_attester_reward"]

    source_reward = policy_input["source_reward"]
    target_reward = policy_input["target_reward"]
    head_reward = policy_input["head_reward"]

    # Calculate total validating rewards
    validating_rewards = (
        block_proposer_reward
        + block_attester_reward
        + source_reward
        + target_reward
        + head_reward
    )

    return "validating_rewards", validating_rewards
