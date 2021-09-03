"""
cadCAD model State Update Block structure, composed of Policy and State Update Functions
"""

import model.parts.ethereum_system as ethereum
import model.parts.pos_incentives as incentives
import model.parts.system_metrics as metrics
import model.parts.validators as validators
from model.system_parameters import parameters
from model.utils import update_from_signal

state_update_block_stages = {
    "description": """
        Transition between stages of network upgrade process
    """,
    "policies": {"upgrade_stages": ethereum.policy_upgrade_stages},
    "variables": {
        "stage": update_from_signal("stage"),
        "timestamp": update_from_signal("timestamp"),
    },
}

state_update_block_ethereum = {
    "description": """
        Environmental Ethereum processes:
        * ETH price update
        * Staking of ETH for new validators
    """,
    "policies": {
        "staking": validators.policy_staking,
    },
    "variables": {
        "eth_price": ethereum.update_eth_price,
        "eth_staked": update_from_signal("eth_staked"),
    },
}

state_update_block_validators = {
    "description": """
        Environmental validator processes:
        * Validator activation queue
        * Validator rotation
        * Validator uptime
    """,
    "policies": {
        "policy_validators": validators.policy_validators,
    },
    "variables": {
        "number_of_validators_in_activation_queue": update_from_signal(
            "number_of_validators_in_activation_queue"
        ),
        "number_of_active_validators": update_from_signal(
            "number_of_active_validators"
        ),
        "number_of_awake_validators": update_from_signal("number_of_awake_validators"),
        "validator_uptime": update_from_signal("validator_uptime"),
    },
}

_state_update_blocks = [
    {
        "description": """
            Average effective balance & base reward
        """,
        "policies": {
            "average_effective_balance": validators.policy_average_effective_balance,
        },
        "variables": {
            "average_effective_balance": update_from_signal(
                "average_effective_balance"
            ),
            "base_reward": incentives.update_base_reward,
        },
    },
    {
        "description": """
            Attestation & sync committee rewards
        """,
        "policies": {
            "attestation": incentives.policy_attestation_rewards,
            "sync_committee": incentives.policy_sync_committee_reward,
        },
        "variables": {
            "source_reward": update_from_signal("source_reward"),
            "target_reward": update_from_signal("target_reward"),
            "head_reward": update_from_signal("head_reward"),
            "sync_reward": update_from_signal("sync_reward"),
        },
    },
    {
        "description": """
            Block proposal reward
        """,
        "policies": {
            "block_proposal": incentives.policy_block_proposal_reward,
        },
        "variables": {
            "block_proposer_reward": update_from_signal("block_proposer_reward"),
        },
    },
    {
        "description": """
            Attestation & sync committee penalties
        """,
        "policies": {
            "attestation": incentives.policy_attestation_penalties,
            "sync_committee": incentives.policy_sync_committee_penalties,
        },
        "variables": {
            "attestation_penalties": update_from_signal("attestation_penalties"),
            "sync_committee_penalties": update_from_signal("sync_committee_penalties"),
        },
    },
    {
        "description": """
            Validating reward & penalty aggregation
        """,
        "policies": {},
        "variables": {
            "validating_rewards": incentives.update_validating_rewards,
            "validating_penalties": incentives.update_validating_penalties,
        },
    },
    {
        "description": """
            Slashing rewards & penalties
        """,
        "policies": {
            "slashing": incentives.policy_slashing,
        },
        "variables": {
            "amount_slashed": update_from_signal("amount_slashed"),
            "whistleblower_rewards": update_from_signal("whistleblower_rewards"),
        },
    },
    {
        "description": """
            EIP-1559 transaction pricing
        """,
        "policies": {
            "eip1559": ethereum.policy_eip1559_transaction_pricing,
        },
        "variables": {
            "base_fee_per_gas": update_from_signal("base_fee_per_gas"),
            "total_base_fee": update_from_signal("total_base_fee"),
            "total_priority_fee_to_miners": update_from_signal(
                "total_priority_fee_to_miners"
            ),
            "total_priority_fee_to_validators": update_from_signal(
                "total_priority_fee_to_validators"
            ),
        },
    },
    {
        "description": """
            Maximum Extractable Value (MEV)
        """,
        "policies": {
            "mev": ethereum.policy_mev,
        },
        "variables": {
            "total_realized_mev_to_miners": update_from_signal(
                "total_realized_mev_to_miners"
            ),
            "total_realized_mev_to_validators": update_from_signal(
                "total_realized_mev_to_validators"
            ),
        },
    },
    {
        "description": """
            Online validator reward aggregation
        """,
        "policies": {
            "calculate_total_online_validator_rewards": metrics.policy_total_online_validator_rewards,
        },
        "variables": {
            "total_online_validator_rewards": update_from_signal(
                "total_online_validator_rewards"
            ),
        },
    },
    {
        "description": """
            Accounting of Ethereum issuance & inflation
        """,
        "policies": {
            "issuance": ethereum.policy_network_issuance,
        },
        "variables": {
            "eth_supply": ethereum.update_eth_supply,
            "supply_inflation": metrics.update_supply_inflation,
            "network_issuance": update_from_signal("network_issuance"),
            "pow_issuance": update_from_signal("pow_issuance"),
        },
    },
    {
        "description": """
            Accounting of validator costs and online validator rewards
        """,
        "post_processing": False,
        "policies": {
            "metric_validator_costs": metrics.policy_validator_costs,
        },
        "variables": {
            "validator_count_distribution": update_from_signal(
                "validator_count_distribution"
            ),
            "validator_hardware_costs": update_from_signal("validator_hardware_costs"),
            "validator_cloud_costs": update_from_signal("validator_cloud_costs"),
            "validator_third_party_costs": update_from_signal(
                "validator_third_party_costs"
            ),
            "validator_costs": update_from_signal("validator_costs"),
            "total_network_costs": update_from_signal("total_network_costs"),
        },
    },
    {
        "description": """
            Accounting of validator yield metrics
        """,
        "post_processing": False,
        "policies": {
            "yields": metrics.policy_validator_yields,
        },
        "variables": {
            "validator_eth_staked": update_from_signal("validator_eth_staked"),
            "validator_revenue": update_from_signal("validator_revenue"),
            "validator_profit": update_from_signal("validator_profit"),
            "validator_revenue_yields": update_from_signal("validator_revenue_yields"),
            "validator_profit_yields": update_from_signal("validator_profit_yields"),
            "total_revenue": update_from_signal("total_revenue"),
            "total_profit": update_from_signal("total_profit"),
            "total_revenue_yields": update_from_signal("total_revenue_yields"),
            "total_profit_yields": update_from_signal("total_profit_yields"),
        },
    },
]

# Conditionally update the order of the State Update Blocks using a ternary operator
_state_update_blocks = (
    # If driving with environmental ETH staked process, structure as follows:
    [
        state_update_block_stages,
        state_update_block_ethereum,
        state_update_block_validators,
    ]
    + _state_update_blocks
    if parameters["eth_staked_process"][0](0, 0) is not None
    # Otherwise, if driving with validator adoption (implied ETH staked) process, switch Ethereum and validator blocks:
    else [
        state_update_block_stages,
        state_update_block_validators,
        state_update_block_ethereum,
    ]
    + _state_update_blocks
)

# Split the state update blocks into those used during the simulation (state_update_blocks)
# and those used in post-processing to calculate the system metrics (post_processing_blocks)
state_update_blocks = [
    block for block in _state_update_blocks if not block.get("post_processing", False)
]
post_processing_blocks = [
    block for block in _state_update_blocks if block.get("post_processing", False)
]
