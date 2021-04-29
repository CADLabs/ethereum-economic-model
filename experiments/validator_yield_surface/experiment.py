import numpy as np

from model.state_variables import eth_staked
from experiments.default import experiment, TIMESTEPS, DELTA_TIME
from experiments.utils import generate_cartesion_product

sweep = generate_cartesion_product({
    "eth_price_samples": np.linspace(start=100, stop=3000, num=10),
    "eth_staked_samples": np.linspace(start=eth_staked, stop=33_600_000, num=10),
})

parameter_overrides = {
    "eth_price_process": [
        lambda run, _timestep: sweep["eth_price_samples"][run]
    ],
    "eth_staked_process": [
        lambda run, _timestep: sweep["eth_staked_samples"][run]
    ]
}

# Override default experiment parameters
experiment.simulations[0].model.params.update(parameter_overrides)
# Set runs to number of combinations in sweep
experiment.simulations[0].runs = len(sweep["eth_price_samples"])
