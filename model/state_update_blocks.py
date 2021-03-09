import model.parts.ethereum as ethereum
import model.parts.validators as validators


state_update_blocks = [
    {
        'policies': {},
        'variables': {
            'eth_price': ethereum.update_eth_price,
            'eth_staked': ethereum.update_eth_staked
        }
    },
    {
        'policies': {
            'policy_validators': validators.policy_validators
        },
        'variables': {
            'number_of_validators': validators.update_number_of_validators,
            'number_of_validators_online': validators.update_number_of_validators_online,
            'number_of_validators_offline': validators.update_number_of_validators_offline,
        }
    }
]
