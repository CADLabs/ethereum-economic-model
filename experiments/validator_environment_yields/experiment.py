import numpy as np
from experiments.default import experiment, TIMESTEPS, DELTA_TIME


eth_price_samples = np.linspace(start=100, stop=3000, num=(TIMESTEPS * DELTA_TIME + 1))

parameter_overrides = {
    "eth_price_process": [
        lambda _run, timestep: eth_price_samples[timestep]
    ],
    "eth_staked_process": [
        lambda _run, _timestep: 524_288,  # From https://beaconscan.com/ as of 20/04/21
        lambda _run, _timestep: 33_600_000,  # From Hoban/Borgers Economic Report
    ]
}

# Override default experiment parameters
experiment.simulations[0].model.params.update(parameter_overrides)
