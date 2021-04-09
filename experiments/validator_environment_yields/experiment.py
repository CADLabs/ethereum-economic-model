import numpy as np
from experiments.default import experiment, TIMESTEPS


eth_price_samples = np.linspace(start=25, stop=1500, num=TIMESTEPS)

parameter_overrides = {
    "eth_price_process": [
        lambda _run, timestep: eth_price_samples[timestep]
    ],
    "eth_staked_process": [
        lambda _run, _timestep: 524_288,
        lambda _run, _timestep: 33_600_000
    ]
}

# Override default experiment parameters
experiment.simulations[0].model.params.update(parameter_overrides)
