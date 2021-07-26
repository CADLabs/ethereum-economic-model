"""
# Genesis ETH Price / ETH Staked Grid Analysis

Creates a cartesian product grid of ETH price and ETH staked processes, for phase-space analyses,
starting from the ETH staked genesis requirement of 524,288 ETH staked.
"""

import numpy as np
import copy

from model.state_variables import eth_staked, eth_price_max
from experiments.default_experiment import experiment, TIMESTEPS, DELTA_TIME
from experiments.utils import generate_cartesian_product
from model.types import Stage


# Make a copy of the default experiment to avoid mutation
experiment = copy.deepcopy(experiment)

sweep = generate_cartesian_product({
    # ETH price range from 100 USD/ETH to the maximum over the last 12 months
    "eth_price_samples": np.linspace(start=100, stop=eth_price_max, num=20),
    # ETH staked range from genesis requirement to current ETH staked
    "eth_staked_samples": np.linspace(start=524_288, stop=eth_staked, num=20),
})

parameter_overrides = {
    "eth_price_process": [
        lambda run, _timestep: sweep["eth_price_samples"][run - 1]
    ],
    "eth_staked_process": [
        lambda run, _timestep: sweep["eth_staked_samples"][run - 1]
    ]
}

# Override default experiment parameters
experiment.simulations[0].model.params.update(parameter_overrides)
# Set runs to number of combinations in sweep
experiment.simulations[0].runs = len(sweep["eth_price_samples"])
# Run single timestep, set unit of time to multiple epochs
experiment.simulations[0].timesteps = 1
experiment.simulations[0].model.params.update({"dt": [TIMESTEPS * DELTA_TIME]})
