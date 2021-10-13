"""
# Extended-time Horizon

Executes a time-domain simulation over a period of 10 years,
over all Ethereum network upgrade stages.
"""

import copy

import model.constants as constants
from model.types import Stage
from experiments.default_experiment import experiment


# Make a copy of the default experiment to avoid mutation
experiment = copy.deepcopy(experiment)

DELTA_TIME = constants.epochs_per_week  # epochs per timestep
SIMULATION_TIME_MONTHS = 12 * 10  # number of months
TIMESTEPS = constants.epochs_per_month * SIMULATION_TIME_MONTHS // DELTA_TIME

parameter_overrides = {
    "stage": [Stage.ALL],
}

# Override default experiment Simulation and System Parameters related to timing
experiment.simulations[0].timesteps = TIMESTEPS
experiment.simulations[0].model.params.update({"dt": [DELTA_TIME]})

# Override default experiment System Parameters
experiment.simulations[0].model.params.update(parameter_overrides)
