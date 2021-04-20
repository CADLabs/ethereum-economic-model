import model.parts.ethereum as ethereum
import model.parts.validators as validators
import model.parts.incentives as incentives
import model.parts.metrics as metrics
from model.utils import update_from_signal


_state_update_blocks = [
    *[{
        "description": """
            Exogenous Ethereum processes:
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
    },
    {
        "description": """
            Validator processes:
            * New validators
            * Online and offline validators
        """,
        "policies": {
            "policy_validators": validators.policy_validators,
        },
        "variables": {
            "number_of_validators_in_activation_queue": update_from_signal("number_of_validators_in_activation_queue"),
            "number_of_validators": update_from_signal("number_of_validators"),
            "number_of_validators_online": update_from_signal(
                "number_of_validators_online"
            ),
            "number_of_validators_offline": update_from_signal(
                "number_of_validators_offline"
            ),
        },
    }][::-1],
    {
        "description": """
            Calculation and update of validator average effective balance & base reward
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
            Sync committee and attestation rewards
        """,
        "policies": {
            "casper_ffg_vote": incentives.policy_attestation_rewards,
            "sync_committee": incentives.policy_sync_committee,
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
            Block proposal rewards
        """,
        "policies": {
            "block_proposal": incentives.policy_block_proposal,
        },
        "variables": {
            "block_proposer_reward": update_from_signal("block_proposer_reward"),
        },
    },
    {
        "description": """
            Total validating rewards and penalties
        """,
        "policies": {
            "penalties": incentives.policy_attestation_penalties,
        },
        "variables": {
            "validating_rewards": incentives.update_validating_rewards,
            "validating_penalties": update_from_signal("validating_penalties"),
        },
    },
    {
        "description": """
            Validator slashing process, rewards, and penalties
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
            Ethereum EIP1559 process
        """,
        "policies": {
            "eip1559": ethereum.policy_eip1559_transaction_pricing,
        },
        "variables": {
            "total_basefee": update_from_signal("total_basefee"),
            "total_tips_to_validators": update_from_signal("total_tips_to_validators"),
        },
    },
    {
        "description": """
            Online validator reward aggregation, and accounting of Ethereum issuance & inflation 
        """,
        "policies": {
            "calculate_total_online_validator_rewards": metrics.policy_total_online_validator_rewards,
            "issuance": ethereum.policy_network_issuance,
        },
        "variables": {
            "total_online_validator_rewards": update_from_signal(
                "total_online_validator_rewards"
            ),
            "eth_supply": ethereum.update_eth_supply,
            "supply_inflation": metrics.update_supply_inflation,
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

# Split the state update blocks into those used during the simulation (state_update_blocks)
# and those used in post-processing to calculate the system metrics (post_processing_blocks)
state_update_blocks = [
    block for block in _state_update_blocks if not block.get("post_processing", False)
]
post_processing_blocks = [
    block for block in _state_update_blocks if block.get("post_processing", False)
]
