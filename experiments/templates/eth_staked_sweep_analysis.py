"""
# ETH Staked Sweep Analysis

Creates a parameter sweep of the ETH staked process, with a static value for ETH price set to
the current maximum ETH price value over the last 6 months from Etherscan.io.
"""

import numpy as np
import copy

from experiments.simulation_configuration import TIMESTEPS, DELTA_TIME
from model.state_variables import eth_staked, eth_supply, eth_price_max
from experiments.default_experiment import experiment

# Make a copy of the default experiment to avoid mutation
experiment = copy.deepcopy(experiment)

eth_staked_samples = np.linspace(
    eth_staked,
    eth_supply * 0.3,  # 30% of current total ETH supply
    50
)

parameter_overrides = {
    "eth_staked_process": [
        lambda run, _timestep: eth_staked_samples[run - 1],
    ],
    "eth_price_process": [
        # A sweep of two fixed ETH price points
        lambda _run, _timestep: 100,
        lambda _run, _timestep: eth_price_max,
    ]
}

# Override default experiment parameters
experiment.simulations[0].model.params.update(parameter_overrides)
# Set runs to number of items in eth_staked_samples
experiment.simulations[0].runs = len(eth_staked_samples)
# Run single timestep, set unit of time to multiple epochs
experiment.simulations[0].timesteps = 1
experiment.simulations[0].model.params.update({"dt": [TIMESTEPS * DELTA_TIME]})
