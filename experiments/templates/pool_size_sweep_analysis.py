"""
# Pool Size Sweep Analysis

Creates a parameter sweep of the avg_pool_size parameter, .
"""

import numpy as np
import copy

import model.constants as constants
from experiments.default_experiment import experiment
from model.system_parameters import pool_validator_indeces
from model.state_variables import validator_count_distribution

# Make a copy of the default experiment to avoid mutation
experiment = copy.deepcopy(experiment)

DELTA_TIME = constants.epochs_per_day # epochs per timestep
SIMULATION_TIME_MONTHS = 5 * 12  # number of months
TIMESTEPS = constants.epochs_per_month * SIMULATION_TIME_MONTHS // DELTA_TIME

pool_size_samples = np.linspace(
    1, 
    200,
    10,
    dtype=int
)


# Calculate inititial number of pools (derived from 'avg_pool_size' parameter list)

nValidatorEnvironments = len(validator_count_distribution)
number_of_pools_list = np.zeros((len(pool_size_samples), nValidatorEnvironments))

for i in range(len(pool_size_samples)): 
    for y in range(nValidatorEnvironments):
        if y in pool_validator_indeces:
            number_of_pools_list[i][y] = np.round(validator_count_distribution[y] / pool_size_samples[i])




parameter_overrides = {
    "avg_pool_size": pool_size_samples,
    "number_of_pools": number_of_pools_list,
    "eth_price_process": [
        lambda _run, _timestep: 2000,
    ]
}

# Override default experiment parameters
experiment.simulations[0].model.params.update(parameter_overrides)
# Set runs 
experiment.simulations[0].runs = 1
# Run single timestep, set unit of time to multiple epochs
experiment.simulations[0].timesteps = TIMESTEPS
experiment.simulations[0].model.params.update({"dt": [DELTA_TIME]})
