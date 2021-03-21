import model.constants as constants


def policy_network_issuance(params, substep, state_history, previous_state):
    # State Variables
    amount_slashed = previous_state['amount_slashed']
    total_basefee = previous_state['total_basefee']
    total_tips_to_validators = previous_state['total_tips_to_validators']
    total_online_validator_rewards = previous_state['total_online_validator_rewards']

    # Calculate network issuance in Gwei and ETH
    network_issuance = total_online_validator_rewards - amount_slashed - total_basefee
    network_issuance -= total_tips_to_validators # total_online_validator_rewards includes tips to validators, which is not issuance
    network_issuance_eth = network_issuance / constants.gwei

    return {
        'network_issuance': network_issuance,
        'network_issuance_eth': network_issuance_eth,
    }

def update_eth_price(params, substep, state_history, previous_state, policy_input):
    # Parameters
    eth_price_process = params['eth_price_process']

    # State Variables
    run = previous_state['run']
    timestep = previous_state['timestep']

    # Get the ETH price sample for the current run and timestep
    eth_price_sample = eth_price_process(run, timestep)

    return 'eth_price', eth_price_sample

def update_eth_staked(params, substep, state_history, previous_state, policy_input):
    eth_staked = previous_state['eth_staked']
    staked_eth = policy_input['staked_eth']

    return 'eth_staked', eth_staked + staked_eth

def update_supply_inflation(params, substep, state_history, previous_state, policy_input):
    eth_supply = previous_state['eth_supply']
    network_issuance_eth = policy_input['network_issuance_eth']

    supply_inflation = (network_issuance_eth * constants.epochs_per_year) / eth_supply
   
    return 'supply_inflation', supply_inflation

def update_eth_supply(params, substep, state_history, previous_state, policy_input):
    eth_supply = previous_state['eth_supply']
    network_issuance_eth = policy_input['network_issuance_eth']

    return 'eth_supply', eth_supply + network_issuance_eth
