import model.parts.ethereum as ethereum
import model.parts.validators as validators
import model.parts.proof_of_stake as proof_of_stake
import model.parts.slashing as slashing
import model.parts.accounting as accounting
import model.parts.eip1559 as eip1559


state_update_blocks = [
    {
        'description': '''
            Exogenous Ethereum processes:
            * ETH price update
            * Staking of ETH for new validators
        ''',
        'policies': {
            'staking': validators.policy_staking,
        },
        'variables': {
            'eth_price': ethereum.update_eth_price,
            'eth_staked': ethereum.update_eth_staked,
        }
    },
    {
       'description': '''
            Validator processes:
            * New validators
            * Online and offline validators
        ''',
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
        'description': '''
            Calculation and update of validator average effective balance & base reward
        ''',
        'policies': {
            'average_effective_balance': validators.policy_average_effective_balance,
        },
        'variables': {
            'average_effective_balance': validators.update_average_effective_balance,
            'base_reward': proof_of_stake.update_base_reward,
        }
    },
    {
        'description': '''
            Beacon chain block proposal and attestation processes, rewards, and penalties
        ''',
        'policies': {
            'block_proposal': proof_of_stake.policy_block_proposal,
            'casper_ffg_vote': proof_of_stake.policy_casper_ffg_vote,
            'lmd_ghost_vote': proof_of_stake.policy_lmd_ghost_vote,
            'penalties': proof_of_stake.policy_penalties,
        },
        'variables': {
            # Casper FFG vote
            'source_reward': proof_of_stake.update_source_reward,
            'target_reward': proof_of_stake.update_target_reward,
            # LMD Ghost vote
            'head_reward': proof_of_stake.update_head_reward,
            'block_attester_reward': proof_of_stake.update_block_attester_reward,
            'block_proposer_reward': proof_of_stake.update_block_proposer_reward,
            # Total validating rewards and penalties
            'validating_rewards': proof_of_stake.update_validating_rewards,
            'validating_penalties': proof_of_stake.update_validating_penalties,
        }
    },
    {
        'description': '''
            Validator slashing process, rewards, and penalties
        ''',
        'policies': {
            'slashing': slashing.policy_slashing,
        },
        'variables': {
            'amount_slashed': slashing.update_amount_slashed,
            'whistleblower_rewards': slashing.update_whistleblower_rewards,
        }
    },
    {
        'description': '''
            EIP1559 process
        ''',
        'policies': {
            'eip1559': eip1559.policy_eip1559,
        },
        'variables': {
            'total_basefee': eip1559.update_total_basefee,
            'total_tips_to_validators': eip1559.update_total_tips_to_validators
        }
    },
    {
        'description': '''
            Accounting of validator costs and online validator rewards
        ''',
        'policies': {
            'validator_costs': accounting.policy_validator_costs,
        },
        'variables': {
            'total_online_validator_rewards': accounting.update_total_online_validator_rewards,
            'validator_count_distribution': accounting.update_validator_count_distribution,
            'validator_hardware_costs': accounting.update_validator_hardware_costs,
            'validator_cloud_costs': accounting.update_validator_cloud_costs,
            'validator_third_party_costs': accounting.update_validator_third_party_costs,
            'validator_costs': accounting.update_validator_costs,
            'total_network_costs': accounting.update_total_network_costs,
        }
    },
    {
        'description': '''
            Accounting of Ethereum issuance, inflation, and validator yields
        ''',
        'policies': {
            'issuance': ethereum.policy_network_issuance,
            'yields': accounting.policy_calculate_yields,
        },
        'variables': {
            'supply_inflation': ethereum.update_supply_inflation,
            'eth_supply': ethereum.update_eth_supply,
            'validator_eth_staked': accounting.update_validator_eth_staked,
            'validator_revenue': accounting.update_validator_revenue,
            'validator_profit': accounting.update_validator_profit,
            'validator_revenue_yields': accounting.update_validator_revenue_yields,
            'validator_profit_yields': accounting.update_validator_profit_yields,
            'total_revenue': accounting.update_total_revenue,
            'total_profit': accounting.update_total_profit,
            'total_revenue_yields': accounting.update_total_revenue_yields,
            'total_profit_yields': accounting.update_total_profit_yields,
        }
    },
]
