"""
Relevant methods from the official [eth2.0-specs](https://github.com/ethereum/eth2.0-specs) specification repo.

* Phase 0: https://github.com/ethereum/eth2.0-specs/blob/dev/specs/phase0/beacon-chain.md
* Altair updates: https://github.com/ethereum/eth2.0-specs/blob/dev/specs/altair/beacon-chain.md
"""

import model.constants as constants
from model.state_variables import StateVariables
from model.system_parameters import Parameters
from model.types import Gwei


# Beacon state accessors


def get_total_active_balance(params: Parameters, state: StateVariables) -> Gwei:
    """
    See https://github.com/ethereum/eth2.0-specs/blob/dev/specs/phase0/beacon-chain.md#get_total_active_balance

    ```python
    def get_total_active_balance(state: BeaconState) -> Gwei:
        '''
        Return the combined effective balance of the active validators.
        Note: ``get_total_balance`` returns ``EFFECTIVE_BALANCE_INCREMENT`` Gwei minimum to avoid divisions by zero.
        '''
        return get_total_balance(state, set(get_active_validator_indices(state, get_current_epoch(state))))
    ```
    """

    # Parameters
    EFFECTIVE_BALANCE_INCREMENT = params["EFFECTIVE_BALANCE_INCREMENT"]
    MAX_EFFECTIVE_BALANCE = params["MAX_EFFECTIVE_BALANCE"]

    # State Variables
    eth_staked = state["eth_staked"]
    number_of_validators = state["number_of_validators"]

    # Calculate total active balance
    total_active_balance = (
        eth_staked * constants.gwei
        - (eth_staked * constants.gwei) % EFFECTIVE_BALANCE_INCREMENT
    )
    max_total_active_balance = MAX_EFFECTIVE_BALANCE * number_of_validators

    total_active_balance = min(total_active_balance, max_total_active_balance)

    return Gwei(max(EFFECTIVE_BALANCE_INCREMENT, total_active_balance))


def integer_squareroot(n):
    """
    Return the largest integer ``x`` such that ``x**2 <= n``.

    See https://benjaminion.xyz/eth2-annotated-spec/phase0/beacon-chain/
    """
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


def get_base_reward_per_increment(params: Parameters, state: StateVariables) -> Gwei:
    """Get the base reward per increment (single validator)"""

    EFFECTIVE_BALANCE_INCREMENT = params["EFFECTIVE_BALANCE_INCREMENT"]
    BASE_REWARD_FACTOR = params["BASE_REWARD_FACTOR"]

    return Gwei(
        EFFECTIVE_BALANCE_INCREMENT
        * BASE_REWARD_FACTOR
        // integer_squareroot(int(get_total_active_balance(params, state)))
    )


def get_base_reward(params: Parameters, state: StateVariables) -> Gwei:
    """Get the base reward for the current epoch"""

    # Parameters
    MAX_EFFECTIVE_BALANCE = params["MAX_EFFECTIVE_BALANCE"]
    EFFECTIVE_BALANCE_INCREMENT = params["EFFECTIVE_BALANCE_INCREMENT"]

    # State Variables
    average_effective_balance = state["average_effective_balance"]

    increments = (
        min(average_effective_balance, MAX_EFFECTIVE_BALANCE)
        // EFFECTIVE_BALANCE_INCREMENT
    )

    return Gwei(increments * get_base_reward_per_increment(params, state))


def get_proposer_reward(params: Parameters, state: StateVariables) -> Gwei:
    """Get the proposer reward as a proportion of the base reward"""

    PROPOSER_REWARD_QUOTIENT = params["PROPOSER_REWARD_QUOTIENT"]
    return Gwei(get_base_reward(params, state) // PROPOSER_REWARD_QUOTIENT)


def get_validator_churn_limit(params: Parameters, state: StateVariables) -> int:
    """
    Return the validator churn limit for the current epoch.

    See https://github.com/ethereum/eth2.0-specs/blob/dev/specs/phase0/beacon-chain.md#get_validator_churn_limit

    ```python
    active_validator_indices = get_active_validator_indices(state, get_current_epoch(state))
    return max(MIN_PER_EPOCH_CHURN_LIMIT, uint64(len(active_validator_indices)) // CHURN_LIMIT_QUOTIENT)
    ```
    """
    # Parameters
    MIN_PER_EPOCH_CHURN_LIMIT = params["MIN_PER_EPOCH_CHURN_LIMIT"]
    CHURN_LIMIT_QUOTIENT = params["CHURN_LIMIT_QUOTIENT"]

    # State Variables
    number_of_validators = state["number_of_validators"]

    return max(MIN_PER_EPOCH_CHURN_LIMIT, number_of_validators // CHURN_LIMIT_QUOTIENT)
