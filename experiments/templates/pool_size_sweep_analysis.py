"""
# Pool Size Sweep Analysis

Creates a parameter sweep of the avg_pool_size parameter, .
"""

import numpy as np
import copy

import model.constants as constants
from experiments.simulation_configuration import TIMESTEPS, DELTA_TIME
from model.state_variables import eth_staked, eth_supply, eth_price_max
from experiments.default_experiment import experiment

# Make a copy of the default experiment to avoid mutation
experiment = copy.deepcopy(experiment)

DELTA_TIME = constants.epochs_per_month  # epochs per timestep
SIMULATION_TIME_MONTHS = 12 * 1  # number of months
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
        lambda _run, _timestep: 1000,
    ]
}

# Override default experiment parameters
experiment.simulations[0].model.params.update(parameter_overrides)
# Set runs to number of items in eth_staked_samples
experiment.simulations[0].runs = 1
# Run single timestep, set unit of time to multiple epochs
experiment.simulations[0].timesteps = 30
experiment.simulations[0].model.params.update({"dt": [TIMESTEPS * DELTA_TIME]})
