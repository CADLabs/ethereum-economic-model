"""
# Pool Size Sweep Analysis

Creates a parameter sweep of the avg_pool_size parameter, .
"""

import numpy as np
import copy

import model.constants as constants
from experiments.default_experiment import experiment

# Make a copy of the default experiment to avoid mutation
experiment = copy.deepcopy(experiment)

DELTA_TIME = constants.epochs_per_month  # epochs per timestep
SIMULATION_TIME_MONTHS = 12 * 10  # number of months
TIMESTEPS = constants.epochs_per_month * SIMULATION_TIME_MONTHS // DELTA_TIME

pool_size_samples = np.linspace(
    0, 
    100,
    100,
    dtype=int
)

parameter_overrides = {
    "avg_pool_size": pool_size_samples,
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
