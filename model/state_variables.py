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
    Stage,
)
from model.system_parameters import validator_environments


# Get number of validator environments for initializing Numpy array size
number_of_validator_environments = len(validator_environments)

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
    stage: Stage = None
    """
    The stage of the network upgrade process.

    By default set to PROOF_OF_STAKE Stage, where EIP1559 is enabled and POW issuance is disabled.

    Otherwise set to ALL Stage, which transitions through each stage, updating the `stage` State Variable.

    See model.types.Stage Enum for further documentation.
    """
    timestamp: datetime = None
    """
    The timestamp for each timestep as a Python `datetime` object, starting from `date_start` Parameter.
    """

    # Ethereum state variables
    eth_price: USD_per_ETH = 0
    """The ETH spot price"""
    eth_supply: ETH = eth_supply
    """The total ETH supply"""
    eth_staked: ETH = eth_staked
    """The total ETH staked as part of the Proof of Stake system"""
    supply_inflation: Percentage = 0
    """The annualized ETH supply inflation"""
    network_issuance: ETH = 0
    """The total network issuance in ETH"""
    pow_issuance: ETH = 0
    """The total Proof of Work issuance in ETH"""

    # Validator state variables
    number_of_validators_in_activation_queue: int = (
        number_of_validators_in_activation_queue
    )
    """The number of validators in activation queue"""
    average_effective_balance: Gwei = 32 * constants.gwei
    """The validator average effective balance"""
    number_of_validators: int = number_of_validators
    """The total number of validators"""
    number_of_validators_online: int = 0
    """The total number of online validators"""
    number_of_validators_offline: int = 0
    """The total number of offline validators"""

    # Reward and penalty state variables
    base_reward: Gwei = 0
    """
    Validator rewards and penalties are calculated in terms of the base reward.
    Under perfect network conditions, each validator should receive 1 base reward per epoch for performing their duties.
    """
    validating_rewards: Gwei = 0
    """The total rewards received for PoS validation (attestation, block proposal, sync vote)"""
    validating_penalties: Gwei = 0
    """The total penalties received for failing to perform PoS validation duties (attestation, sync vote)"""
    source_reward: Gwei = 0
    """The total rewards received for getting a source vote in time and correctly"""
    target_reward: Gwei = 0
    """The total rewards received for getting a target vote in time and correctly"""
    head_reward: Gwei = 0
    """The total rewards received for getting a head vote in time and correctly"""
    block_proposer_reward: Gwei = 0
    """The total rewards received for successfully proposing a block"""
    sync_reward: Gwei = 0
    """The total rewards received for attesting as part of a sync committee"""
    attestation_penalties: Gwei = 0
    """The total penalties received for failing to perform attestation duties"""
    sync_committee_penalties: Gwei = 0
    """The total penalties received for failing to perform sync committee duties"""

    # Slashing state variables
    amount_slashed: Gwei = 0
    """The total penalties applied for slashable offences"""
    whistleblower_rewards: Gwei = 0
    """The total rewards received as a proportion of the effective balance of the slashed validators"""

    # EIP1559 state variables
    basefee: Gwei_per_Gas = 1
    """The basefee burned, in Gwei per gas, for each transaction, dynamically updated for each block"""
    total_basefee: Gwei = 0
    """The total basefee burned"""
    total_tips_to_miners: Gwei = 0
    """"The total tips to miners pre-merge for transactions included in blockspace"""
    total_tips_to_validators: Gwei = 0
    """"The total tips to validators post-merge for transactions included in blockspace"""

    # System metric state variables
    validator_eth_staked: np.ndarray = np.zeros(
        (number_of_validator_environments, 1), dtype=int
    )
    """The ETH staked per validator environment"""
    validator_revenue: np.ndarray = np.zeros(
        (number_of_validator_environments, 1), dtype=int
    )
    """The total revenue (income received) for performing PoS duties per validator environment"""
    validator_profit: np.ndarray = np.zeros(
        (number_of_validator_environments, 1), dtype=int
    )
    """The total profit (income received - costs) per validator environment"""
    validator_revenue_yields: np.ndarray = np.zeros(
        (number_of_validator_environments, 1), dtype=int
    )
    """The total annualized revenue (income received) yield (percentage of investment amount)
    per validator environment"""
    validator_profit_yields: np.ndarray = np.zeros(
        (number_of_validator_environments, 1), dtype=int
    )
    """The total annualized profit (income received - costs) yield (percentage of investment amount)
    per validator environment"""

    validator_count_distribution: np.ndarray = np.zeros(
        (number_of_validator_environments, 1), dtype=int
    )
    """The total number of validators per validator environment"""
    validator_hardware_costs: np.ndarray = np.zeros(
        (number_of_validator_environments, 1), dtype=USD
    )
    """The total validator hardware operation costs per validator environment"""
    validator_cloud_costs: np.ndarray = np.zeros(
        (number_of_validator_environments, 1), dtype=USD
    )
    """The total validator cloud operation costs per validator environment"""
    validator_third_party_costs: np.ndarray = np.zeros(
        (number_of_validator_environments, 1), dtype=USD
    )
    """The total validator third-party fee costs validator environment"""
    validator_costs: np.ndarray = np.zeros(
        (number_of_validator_environments, 1), dtype=USD
    )
    """The total validator costs validator environment"""

    total_online_validator_rewards: Gwei = 0
    """The total rewards received by online validators"""
    total_network_costs: USD = 0
    """The total validator operational costs for securing the network"""
    total_revenue: USD = 0
    """The total validator revenue (income received)"""
    total_profit: USD = 0
    """The total validator profit (income received - costs)"""
    total_revenue_yields: Percentage = 0
    """Annualized revenue (income received) for all validators"""
    total_profit_yields: Percentage = 0
    """Annualized profit (income received - costs) for all validators"""


# Initialize State Variables instance with default values
initial_state = StateVariables().__dict__
