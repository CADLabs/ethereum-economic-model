"""
# ETH Price Sweep Analysis

Creates a parameter sweep of the ETH price process,
with a static value for ETH staked set to the current ETH staked value from Beaconcha.in.
"""

import numpy as np
import copy

from model.state_variables import eth_staked, eth_price_max
from model.types import Stage
from experiments.default_experiment import experiment, TIMESTEPS, DELTA_TIME


# Make a copy of the default experiment to avoid mutation
experiment = copy.deepcopy(experiment)

# ETH price range from 100 USD/ETH to the maximum over the last 12 months
eth_price_samples = np.linspace(start=100, stop=eth_price_max, num=50)

parameter_overrides = {
    "eth_price_process": [
        lambda run, _timestep: eth_price_samples[run - 1]
    ],
    "eth_staked_process": [
        lambda _run, _timestep: eth_staked,
    ],
}

# Override default experiment parameters
experiment.simulations[0].model.params.update(parameter_overrides)
# Set runs to number of combinations in sweep
experiment.simulations[0].runs = len(eth_price_samples)
# Run single timestep, set unit of time to multiple epochs
experiment.simulations[0].timesteps = 1
experiment.simulations[0].model.params.update({"dt": [TIMESTEPS * DELTA_TIME]})
