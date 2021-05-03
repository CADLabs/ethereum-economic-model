from model.types import Phase
import model.constants as constants
import model.simulation_configuration as simulation_configuration
from model.parameters import create_eth_price_process

from experiments.default import experiment


DELTA_TIME = constants.epochs_per_day  # epochs per timestep
SIMULATION_TIME_MONTHS = 12 * 5  # number of months
TIMESTEPS = constants.epochs_per_month * SIMULATION_TIME_MONTHS // DELTA_TIME

eth_price_samples = create_eth_price_process(TIMESTEPS, DELTA_TIME)

parameter_overrides = {
    "phase": [Phase.ALL],
    "eth_price_process": [lambda _run, timestep: eth_price_samples[timestep]],
}

experiment.simulations[0].timesteps = TIMESTEPS
# Override default experiment System Parameters
experiment.simulations[0].model.params.update(parameter_overrides)
