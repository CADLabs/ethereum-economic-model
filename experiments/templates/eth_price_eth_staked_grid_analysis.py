"""
# ETH Price / ETH Staked Grid Analysis

Creates a cartesian product grid of ETH price and ETH staked processes, for phase-space analyses.
"""

import numpy as np
import copy
from radcad.utils import generate_cartesian_product_parameter_sweep

from model.state_variables import eth_staked, eth_supply, eth_price_max
from experiments.default_experiment import experiment, TIMESTEPS, DELTA_TIME


# Make a copy of the default experiment to avoid mutation
experiment = copy.deepcopy(experiment)

sweep = generate_cartesian_product_parameter_sweep({
    # ETH price range from 100 USD/ETH to the maximum over the last 12 months
    "eth_price_samples": np.linspace(start=100, stop=eth_price_max, num=20),
    # ETH staked range from current ETH staked to minimum of 2 x ETH staked and 30% of total ETH supply
    "eth_staked_samples": np.linspace(start=eth_staked, stop=min(eth_staked * 2, eth_supply * 0.3), num=20),
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
