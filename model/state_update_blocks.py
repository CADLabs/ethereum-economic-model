import model.parts.ethereum as ethereum
import model.parts.validators as validators
import model.parts.proof_of_stake as proof_of_stake
import model.parts.metrics as metrics
from model.utils import update_from_signal


state_update_blocks = [
    {
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
            "eth_staked": validators.update_eth_staked,
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
            "number_of_validators": update_from_signal("number_of_validators"),
            "number_of_validators_online": update_from_signal(
                "number_of_validators_online"
            ),
            "number_of_validators_offline": update_from_signal(
                "number_of_validators_offline"
            ),
        },
    },
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
            "base_reward": proof_of_stake.update_base_reward,
        },
    },
    {
        "description": """
            Beacon chain block proposal and attestation processes, rewards, and penalties
        """,
        "policies": {
            "block_proposal": proof_of_stake.policy_block_proposal,
            "casper_ffg_vote": proof_of_stake.policy_casper_ffg_vote,
            "lmd_ghost_vote": proof_of_stake.policy_lmd_ghost_vote,
            "penalties": proof_of_stake.policy_penalties,
        },
        "variables": {
            # Casper FFG vote
            "source_reward": update_from_signal("source_reward"),
            "target_reward": update_from_signal("target_reward"),
            # LMD Ghost vote
            "head_reward": update_from_signal("head_reward"),
            "block_attester_reward": update_from_signal("block_attester_reward"),
            "block_proposer_reward": update_from_signal("block_proposer_reward"),
            # Total validating rewards and penalties
            "validating_rewards": proof_of_stake.update_validating_rewards,
            "validating_penalties": update_from_signal("validating_penalties"),
        },
    },
    {
        "description": """
            Validator slashing process, rewards, and penalties
        """,
        "policies": {
            "slashing": proof_of_stake.policy_slashing,
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
            "eip1559": ethereum.policy_eip1559,
        },
        "variables": {
            "total_basefee": update_from_signal("total_basefee"),
            "total_tips_to_validators": update_from_signal("total_tips_to_validators"),
        },
    },
    {
        "description": """
            Online validator reward aggregation
        """,
        "policies": {},
        "variables": {
            "total_online_validator_rewards": metrics.update_total_online_validator_rewards,
        }
    },
    {
        "description": """
            Accounting of validator costs and online validator rewards
        """,
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
            Accounting of Ethereum issuance, inflation, and validator yields
        """,
        "policies": {
            "issuance": ethereum.policy_network_issuance,
            "yields": metrics.policy_calculate_yields,
        },
        "variables": {
            # State Updates
            "eth_supply": ethereum.update_eth_supply,
            # Metrics
            "supply_inflation": metrics.update_supply_inflation,
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
