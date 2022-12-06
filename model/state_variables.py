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
import data.api.etherscan as etherscan
import model.system_parameters as system_parameters
from model.system_parameters import validator_environments
from model.types import (
    Gwei,
    Gwei_per_Gas,
    ETH,
    POLYGN,
    USD,
    USD_per_ETH,
    Percentage,
    Stage,
    List,
)
from data.historical_values import eth_price_mean, eth_price_min, eth_price_max


# Get number of validator environments for initializing Numpy array size
number_of_validator_environments = len(validator_environments)

# Initial state from external live data source, setting a default in case API call fails
number_of_active_validators: int = 100
polygn_staked: POLYGN = 3_000_000_000e9 / constants.gwei
polygn_supply: POLYGN = (
    etherscan.get_polygn_supply(default=10_000_000_000e18) / constants.wei
)


@dataclass
class StateVariables:
    """State Variables
    Each State Variable is defined as:
    state variable key: state variable type = default state variable value
    """

    # TODO: need to move to system parameters in order to be able to change it and run experiments
    # Network state variables
    PUBLIC_CHAINS_CNT: int = 1
    """Number of public chains"""
    PRIVATE_CHAINS_CNT: int = 1
    """Number of private chains"""
    CHAINS_CNT: int = PUBLIC_CHAINS_CNT + PRIVATE_CHAINS_CNT
    """Total number of chains"""

    # Time state variables
    stage: Stage = None
    """
    The stage of the network upgrade process.

    See "stage" System Parameter in model.system_parameters
    & model.types.Stage Enum for further documentation.
    """
    timestamp: datetime = None
    """
    The timestamp for each timestep as a Python `datetime` object, starting from `date_start` Parameter.
    """

    # POLYGN state variables
    polygn_price: USD_per_ETH = 1.0
    """The POLYGNspot price"""
    polygn_supply: POLYGN = polygn_supply
    """The total POLYGN supply"""
    polygn_staked: POLYGN = polygn_staked
    """The total POLYGN staked as part of the Proof of Stake system"""
    supply_inflation: Percentage = 0
    """The annualized POLYGN supply inflation rate"""
    network_issuance: POLYGN = 0
    """The total network issuance in ETH"""

    # Validator state variables
    number_of_validators_in_activation_queue: int = 0
    """The number of validators in activation queue"""
    ## TODO: need to fix the max cap of average effective balance. 
    average_effective_balance: Gwei = 30_000_000 * constants.gwei
    """The validator average effective balance"""
    number_of_active_validators: int = number_of_active_validators
    """The total number of active validators"""
    number_of_awake_validators: int = min(
        system_parameters.parameters["MAX_VALIDATOR_COUNT"][0] or float("inf"),
        number_of_active_validators,
    )
    """The total number of awake validators"""
    validator_uptime: Percentage = 1
    """The combination of validator internet, power, and technical uptime, as a percentage"""

    # Reward and penalty state variables
    base_reward: Gwei = 0
    """
    Validator rewards and penalties are calculated in terms of the base reward.
    Under perfect network conditions, each validator should receive 1 base reward per epoch for performing their duties.
    """
    total_inflation_to_validators: Gwei = 0
    """
    The total inflation to validators
    """

    # Slashing state variables
    amount_slashed: List[Gwei] = np.zeros(
        CHAINS_CNT,
        dtype=int,
    )
    """The total penalties applied for slashable offences"""

    # EIP-1559 state variables
    base_fee_per_gas: Gwei_per_Gas = 1
    """The base fee burned, in Gwei per gas, dynamically updated for each block"""
    total_public_base_fee: Gwei = np.zeros(
        (PUBLIC_CHAINS_CNT,number_of_validator_environments)
    )
    """The total base fee burned for all transactions included in blockspace in the public chains"""
    total_private_base_fee: Gwei = np.zeros(
        (PRIVATE_CHAINS_CNT,number_of_validator_environments)
    )
    """The total base fee burned for all transactions included in blockspace in the private chains"""
    total_priority_fee_to_validators: Gwei = np.zeros(
        CHAINS_CNT
    )
    """"The total priority fee to validators post Proof-of-Stake for all transactions included in blockspace"""

    # Treasury state variables
    private_base_fee_to_domain_treasury: Gwei = 0
    """
    The total base fee donated for all transactions included in blockspace in the private chains
    to the domain treasury
    """
    public_base_fee_to_domain_treasury: Gwei = 0
    """
    The total base fee donated for all transactions included in blockspace in the public chains
    to the domain treasury
    """

    # System metric state variables
    validator_polygn_staked: np.ndarray = np.zeros(
        (number_of_validator_environments, 1), dtype=int
    )
    """The POLYGN staked per validator environment"""
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
    """The total annualized revenue (income received) yields (percentage of investment amount)
    per validator environment"""
    validator_profit_yields: np.ndarray = np.zeros(
        (number_of_validator_environments, 1), dtype=int
    )
    """The total annualized profit (income received - costs) yields (percentage of investment amount)
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

    domain_treasury_balance_unlocked: Gwei = 0
    """The total unlocked treasury balance"""
    domain_treasury_balance_locked: Gwei = 2_000_000_000 * constants.gwei
    """
    The total locked treasury balance. Initial fund is 2B POLYGN.
    """
    private_treasury_balance: List[Gwei] = np.zeros(
        PRIVATE_CHAINS_CNT
    )
    """The total private chain treasury balance"""


# Initialize State Variables instance with default values
initial_state = StateVariables().__dict__
