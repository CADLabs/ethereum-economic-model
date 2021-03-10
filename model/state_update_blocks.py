import model.parts.ethereum as ethereum
import model.parts.validators as validators
import model.parts.proof_of_stake as proof_of_stake
import model.parts.slashing as slashing
import model.parts.accounting as accounting
import model.parts.eip1559 as eip1559


state_update_blocks = [
    {
        'policies': {},
        'variables': {
            'eth_price': ethereum.update_eth_price,
            'eth_staked': ethereum.update_eth_staked,
        }
    },
    {
        'policies': {
            'policy_validators': validators.policy_validators,
        },
        'variables': {
            'number_of_validators': validators.update_number_of_validators,
            'number_of_validators_online': validators.update_number_of_validators_online,
            'number_of_validators_offline': validators.update_number_of_validators_offline,
        }
    },
    {
        'policies': {},
        'variables': {
            'average_effective_balance': validators.update_average_effective_balance,
        }
    },
    {
        'policies': {},
        'variables': {
            'base_reward': proof_of_stake.update_base_reward,
        }
    },
    {
        'policies': {
            'casper_ffg_vote': proof_of_stake.policy_casper_ffg_vote,
            'lmd_ghost_vote': proof_of_stake.policy_lmd_ghost_vote,
            'block_proposal': proof_of_stake.policy_block_proposal,
        },
        'variables': {
            # Casper FFG vote
            'ffg_source_reward': proof_of_stake.update_ffg_source_reward,
            'ffg_target_reward': proof_of_stake.update_ffg_target_reward,
            # LMD Ghost vote
            'ffg_head_reward': proof_of_stake.update_ffg_head_reward,
            'block_attester_reward': proof_of_stake.update_block_attester_reward,
            'block_proposer_reward': proof_of_stake.update_block_proposer_reward,
            # Total validating rewards
            'validating_rewards': proof_of_stake.update_validating_rewards,
        }
    },
    {
        'policies': {
            'penalties': proof_of_stake.policy_penalties,
            'slashing': slashing.policy_slashing,
        },
        'variables': {
            'penalties': proof_of_stake.update_penalties,
            'amount_slashed': slashing.update_amount_slashed,
            'whistleblower_rewards': slashing.update_whistleblower_rewards,
        }
    },
    {
        'policies': {
            'eip1559': eip1559.policy_eip1559,
        },
        'variables': {
            'total_basefee': eip1559.update_total_basefee,
            'total_tips_to_validators': eip1559.update_total_tips_to_validators
        }
    },
    {
        'policies': {
            'issuance': ethereum.policy_network_issuance,
            'yields': accounting.policy_calculate_yields,
        },
        'variables': {
            'supply_inflation': ethereum.update_supply_inflation,
            'eth_supply': ethereum.update_eth_supply,
            'total_revenue': accounting.update_total_revenue,
            'total_profit': accounting.update_total_profit,
            'revenue_yields': accounting.update_revenue_yields,
            'profit_yields': accounting.update_profit_yields,
        }
    },
]
