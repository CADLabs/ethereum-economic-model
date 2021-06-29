import model.constants as constants

from model.system_parameters import parameters
from radcad.utils import generate_cartesian_product_parameter_sweep


def sweep_half_double_value(param):
    param.append([param[0] * 0.5, param[0] * 2])
    return param

parameters['eth_price_process'] = [
    100, 500, 1000, 2500, 5000, 10000
]
parameters['validator_process'].append([
    lambda _run, _timestep: 3 * 0.5,
    lambda _run, _timestep: 3 * 2
])
sweep_half_double_value(parameters['daily_pow_issuance'])
sweep_half_double_value(parameters['BASE_REWARD_FACTOR'])
sweep_half_double_value(parameters['MAX_EFFECTIVE_BALANCE'])
# parameters['EFFECTIVE_BALANCE_INCREMENT']
sweep_half_double_value(parameters['PROPOSER_REWARD_QUOTIENT'])
sweep_half_double_value(parameters['WHISTLEBLOWER_REWARD_QUOTIENT'])
sweep_half_double_value(parameters['MIN_SLASHING_PENALTY_QUOTIENT'])
sweep_half_double_value(parameters['PROPORTIONAL_SLASHING_MULTIPLIER'])
sweep_half_double_value(parameters['TIMELY_HEAD_WEIGHT'])
sweep_half_double_value(parameters['TIMELY_SOURCE_WEIGHT'])
sweep_half_double_value(parameters['TIMELY_TARGET_WEIGHT'])
sweep_half_double_value(parameters['SYNC_REWARD_WEIGHT'])
sweep_half_double_value(parameters['PROPOSER_WEIGHT'])
sweep_half_double_value(parameters['WEIGHT_DENOMINATOR'])
sweep_half_double_value(parameters['MIN_PER_EPOCH_CHURN_LIMIT'])
sweep_half_double_value(parameters['CHURN_LIMIT_QUOTIENT'])
sweep_half_double_value(parameters['BASE_FEE_MAX_CHANGE_DENOMINATOR'])
sweep_half_double_value(parameters['ELASTICITY_MULTIPLIER'])
parameters['validator_uptime_process'].append([
    lambda _run, _timestep: 0.70,
    lambda _run, _timestep: 1,
])
sweep_half_double_value(parameters['slashing_events_per_1000_epochs'])
parameters['eip1559_basefee_process'].append([
    lambda _run, _timestep: 100,
    lambda _run, _timestep: 50,
])
parameters['eip1559_tip_process'].append([
    lambda _run, _timestep: 1,
    lambda _run, _timestep: 50,
])
parameters['gas_target_process'].append([
    lambda _run, _timestep: 15e6 * 0.5,
    lambda _run, _timestep: 15e6 * 2
])

sweep = generate_cartesian_product_parameter_sweep(parameters)

print(len(sweep[0]))
