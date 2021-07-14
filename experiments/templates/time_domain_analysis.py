"""
# Time Domain Analysis

Executes a time-domain simulation over a long time period of 5 years,
over all Ethereum network upgrade stages.
"""

import copy

import model.constants as constants
from model.stochastic_processes import create_stochastic_process_realizations
from model.types import Stage
from experiments.default_experiment import experiment
from data.historical_values import df_ether_supply


# Make a copy of the default experiment to avoid mutation
experiment = copy.deepcopy(experiment)

DELTA_TIME = constants.epochs_per_day  # epochs per timestep
SIMULATION_TIME_MONTHS = 12 * 5  # number of months
TIMESTEPS = constants.epochs_per_month * SIMULATION_TIME_MONTHS // DELTA_TIME

# Generate stochastic process realizations
eth_price_samples = create_stochastic_process_realizations("eth_price_samples", timesteps=TIMESTEPS, dt=DELTA_TIME)

parameter_overrides = {
    "stage": [Stage.ALL],
    "eth_price_process": [lambda run, timestep: eth_price_samples[run - 1][timestep]],
    "daily_pow_issuance": [12_300]
}

initial_state_overrides = {
    "eth_supply": df_ether_supply['eth_supply'].tolist()[-1],
}


# Override default experiment Simulation and System Parameters related to timing
experiment.simulations[0].timesteps = TIMESTEPS
experiment.simulations[0].model.params.update({"dt": [DELTA_TIME]})

# Override default experiment System Parameters
experiment.simulations[0].model.params.update(parameter_overrides)

# Override default experiemnt Initial State
experiment.simulations[0].model.initial_state.update(initial_state_overrides)
