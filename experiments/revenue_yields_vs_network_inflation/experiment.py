import numpy as np

import model.simulation_configuration as simulation
from experiments.default import experiment


eth_staked_samples = np.linspace(
    524_288,  # From https://beaconscan.com/ as of 20/04/21
    33_600_000,  # From Hoban/Borgers Economic Report
    simulation.TIMESTEPS * simulation.DELTA_TIME + 1
)
eth_staked_process=[None],

parameter_overrides = {
    "eth_staked_process": [
        lambda _run, timestep: eth_staked_samples[timestep],
    ],
    "eth_price_process": [
        # A sweep of two fixed ETH price points
        lambda _run, _timestep: 100,
        lambda _run, _timestep: 3000,
    ]
}

# Override default experiment parameters
experiment.simulations[0].model.params.update(parameter_overrides)
