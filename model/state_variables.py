"""
Definition of State Variables, their types, and default values.

By using a dataclass to represent the State Variables:
* We can use types for Python type hints
* Set default values
* Ensure that all State Variables are initialized
"""


import numpy as np
from dataclasses import dataclass
from datetime import datetime

import model.constants as constants
from model.types import (
    Gwei,
    Gwei_per_Gas,
    ETH,
    USD,
    USD_per_ETH,
    Percentage,
    Uninitialized,
    Phase,
)
from model.parameters import validator_types


# Get number of validator types for initializing Numpy array size
number_of_validator_types = len(validator_types)

# Intial state from external live data source
# Updated from https://beaconscan.com/ as of 20/04/21
number_of_validators = 120_894
number_of_validators_in_activation_queue = 230
eth_staked = 3_868_555
# Updated from https://etherscan.io/chart/ethersupplygrowth as of 20/04/21
eth_supply = 115_538_828


@dataclass
class StateVariables:
    """State Variables
    Each State Variable is defined as:
    state variable key: state variable type = default state variable value
    """

    # Time state variables
    phase: Phase = None
    """
    Keeps track of the current Phase in the
    system phase finite-state machine.
    """
    timestamp: datetime = None

    # Ethereum state variables
    eth_price: USD_per_ETH = 0
    eth_supply: ETH = eth_supply
    eth_staked: ETH = eth_staked
    supply_inflation: Percentage = 0
    pow_issuance: ETH = 0
    """Proof of Work issuance in ETH"""

    # Validator state variables
    number_of_validators_in_activation_queue: int = (
        number_of_validators_in_activation_queue
    )
    average_effective_balance: Gwei = 32 * constants.gwei
    number_of_validators: int = number_of_validators
    number_of_validators_online: int = 0
    number_of_validators_offline: int = 0

    # Reward and penalty state variables
    base_reward: Gwei = 0
    validating_rewards: Gwei = 0
    validating_penalties: Gwei = 0
    source_reward: Gwei = 0
    target_reward: Gwei = 0
    head_reward: Gwei = 0
    block_proposer_reward: Gwei = 0
    sync_reward: Gwei = 0

    # Slashing state variables
    amount_slashed: Gwei = 0
    whistleblower_rewards: Gwei = 0

    # EIP1559 state variables
    basefee: Gwei_per_Gas = 1
    total_basefee: Gwei = 0
    total_tips_to_validators: Gwei = 0

    # System metric state variables
    validator_eth_staked: np.ndarray = np.zeros(
        (number_of_validator_types, 1), dtype=int
    )
    validator_revenue: np.ndarray = np.zeros((number_of_validator_types, 1), dtype=int)
    validator_profit: np.ndarray = np.zeros((number_of_validator_types, 1), dtype=int)
    validator_revenue_yields: np.ndarray = np.zeros(
        (number_of_validator_types, 1), dtype=int
    )
    validator_profit_yields: np.ndarray = np.zeros(
        (number_of_validator_types, 1), dtype=int
    )

    total_online_validator_rewards: Gwei = 0
    total_revenue: USD = 0
    total_profit: USD = 0
    total_revenue_yields: Percentage = 0
    total_profit_yields: Percentage = 0

    validator_count_distribution: np.ndarray = np.zeros(
        (number_of_validator_types, 1), dtype=int
    )
    validator_hardware_costs: np.ndarray = np.zeros(
        (number_of_validator_types, 1), dtype=USD
    )
    validator_cloud_costs: np.ndarray = np.zeros(
        (number_of_validator_types, 1), dtype=USD
    )
    validator_third_party_costs: np.ndarray = np.zeros(
        (number_of_validator_types, 1), dtype=USD
    )
    validator_costs: np.ndarray = np.zeros((number_of_validator_types, 1), dtype=USD)
    total_network_costs: USD = 0


# Initialize State Variables instance with default values
initial_state = StateVariables().__dict__
