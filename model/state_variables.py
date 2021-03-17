from typing import TypedDict
import model.constants as constants
from model.types import Gwei, ETH, USD, USD_per_ETH, Percentage


class StateVariables(TypedDict, total=True):
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

    # Casper FFG state variables
    source_reward: Gwei
    target_reward: Gwei

    # LMD Ghost state variables
    head_reward: Gwei
    block_attester_reward: Gwei
    block_proposer_reward: Gwei

    # Slashing state variables
    amount_slashed: Gwei
    whistleblower_rewards: Gwei

    # EIP1559 state variables
    total_basefee: Gwei
    total_tips_to_validators: Gwei

    # Accounting state variables
    total_revenue: USD
    total_profit: USD
    revenue_yields: USD
    profit_yields: USD


initial_state: StateVariables = {
    # NOTE for states that are either dependent on parameters for initialization, or are stochastic processes, is initializing them here to zero and in state update function intuitive?
    # NOTE one option: distinction of initial state vs. state variables, with state_variables.update(initial_state)
    'eth_price': 0,
    'eth_supply':  112_000_000,
    'eth_staked': 0,
    'supply_inflation': 0,

    'average_effective_balance': 32 * constants.gwei,
    # NOTE See comment above re. initialization
    # Initialized in state update function
    'number_of_validators': 0,
    'number_of_validators_online': 0,
    'number_of_validators_offline': 0,

    'base_reward': 0,
    'validating_rewards': 0,
    'validating_penalties': 0,

    'source_reward': 0,
    'target_reward': 0,

    'head_reward': 0,
    'block_attester_reward': 0,
    'block_proposer_reward': 0,

    'amount_slashed': 0,
    'whistleblower_rewards': 0,

    'total_basefee': 0,
    'total_tips_to_validators': 0,

    'total_revenue': 0,
    'total_profit': 0,
    'revenue_yields': 0,
    'profit_yields': 0,
}
