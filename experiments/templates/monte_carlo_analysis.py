import copy

from model.types import Stage
import model.constants as constants
from model.stochastic_processes import create_stochastic_process_realizations
from experiments.default_experiment import experiment

# Make a copy of the default experiment to avoid mutation
experiment = copy.deepcopy(experiment)

DELTA_TIME = constants.epochs_per_day  # epochs per timestep
SIMULATION_TIME_MONTHS = 12  # number of months
TIMESTEPS = constants.epochs_per_month * SIMULATION_TIME_MONTHS // DELTA_TIME

# Generate stochastic process realizations
MONTE_CARLO_RUNS = 5
eth_price_samples = create_stochastic_process_realizations("eth_price_samples")
eth_price_samples = create_stochastic_process_realizations("validator_samples")
eth_price_samples = create_stochastic_process_realizations("validator_uptime_samples")


parameter_overrides = {
    "stage": [Stage.ALL],
    "eth_price_process": [lambda run, timestep: eth_price_samples[run - 1][timestep]],
    "validator_process": [lambda run, timestep: validator_samples[run - 1][timestep]],
    "validator_uptime_process": [lambda run, timestep: validator_uptime_samples[run - 1][timestep]]
}

experiment.simulations[0].runs = MONTE_CARLO_RUNS
experiment.simulations[0].timesteps = TIMESTEPS
# Override default experiment System Parameters
experiment.simulations[0].model.params.update(parameter_overrides)
