import numpy as np

import model.constants as constants
from model.types import (
    Gwei,
    ETH,
    USD,
    USD_per_ETH,
    Percentage,
    Uninitialized,
    TypedDict,
    BeaconState
)
from model.parameters import validator_types


class StateVariables(TypedDict, total=True):
    # BeaconState
    beacon_state: BeaconState

    # Ethereum state variables
    eth_price: USD_per_ETH
    eth_supply: ETH
    eth_staked: ETH
    supply_inflation: Percentage

    # Validator state variables
    average_effective_balance: Gwei
    number_of_validators: int
    number_of_validators_online: int
    number_of_validators_offline: int

    # Reward and penalty state variables
    base_reward: Gwei
    validating_rewards: Gwei
    validating_penalties: Gwei
    source_reward: Gwei
    target_reward: Gwei
    head_reward: Gwei
    block_proposer_reward: Gwei
    sync_reward: Gwei

    # Slashing state variables
    amount_slashed: Gwei
    whistleblower_rewards: Gwei

    # EIP1559 state variables
    total_basefee: Gwei
    total_tips_to_validators: Gwei

    # System metric state variables
    validator_eth_staked: np.ndarray
    validator_revenue: np.ndarray
    validator_profit: np.ndarray
    validator_revenue_yields: np.ndarray
    validator_profit_yields: np.ndarray

    total_online_validator_rewards: Gwei
    total_revenue: USD
    total_profit: USD
    total_revenue_yields: Percentage
    total_profit_yields: Percentage

    validator_count_distribution: np.ndarray
    validator_hardware_costs: np.ndarray
    validator_cloud_costs: np.ndarray
    validator_third_party_costs: np.ndarray
    validator_costs: np.ndarray
    total_network_costs: USD


# Get number of validator types for initializing Numpy array size
number_of_validator_types = len(validator_types)

# TODO use np.nan for unintialized/unknown initial values
# NOTE https://numpy.org/doc/stable/reference/generated/numpy.nan_to_num.html

initial_state = StateVariables(
    eth_price=0,
    eth_supply=112_000_000,
    eth_staked=0,
    supply_inflation=0,
    average_effective_balance=32 * constants.gwei,
    number_of_validators=0,
    number_of_validators_online=0,
    number_of_validators_offline=0,
    base_reward=0,
    validating_rewards=0,
    validating_penalties=0,
    source_reward=0,
    target_reward=0,
    head_reward=0,
    block_proposer_reward=0,
    sync_reward=0,
    amount_slashed=0,
    whistleblower_rewards=0,
    total_basefee=0,
    total_tips_to_validators=0,
    validator_eth_staked=np.zeros((number_of_validator_types, 1), dtype=int),
    validator_revenue=np.zeros((number_of_validator_types, 1), dtype=int),
    validator_profit=np.zeros((number_of_validator_types, 1), dtype=int),
    validator_revenue_yields=np.zeros((number_of_validator_types, 1), dtype=int),
    validator_profit_yields=np.zeros((number_of_validator_types, 1), dtype=int),
    total_online_validator_rewards=0,
    total_revenue=0,
    total_profit=0,
    total_revenue_yields=0,
    total_profit_yields=0,
    validator_count_distribution=np.zeros((number_of_validator_types, 1), dtype=int),
    validator_hardware_costs=np.zeros((number_of_validator_types, 1), dtype=int),
    validator_cloud_costs=np.zeros((number_of_validator_types, 1), dtype=int),
    validator_third_party_costs=np.zeros((number_of_validator_types, 1), dtype=int),
    validator_costs=np.zeros((number_of_validator_types, 1), dtype=int),
    total_network_costs=0,
)
