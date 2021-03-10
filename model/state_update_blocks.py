import model.parts.ethereum as ethereum
import model.parts.validators as validators
import model.parts.proof_of_stake as proof_of_stake
import model.parts.slashing as slashing


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
            'penalties': proof_of_stake.policy_penalties,
            'slashing': slashing.policy_slashing,
        },
        'variables': {
            'penalties': proof_of_stake.update_penalties,
            'amount_slashed': slashing.update_amount_slashed,
            'whistleblower_rewards': slashing.update_whistleblower_rewards,
        }
    },
]
