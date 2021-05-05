import numpy as np

from model.state_variables import eth_staked
from experiments.default import experiment, TIMESTEPS, DELTA_TIME
from experiments.utils import generate_cartesion_product
from model.types import Phase


sweep = generate_cartesion_product({
    "eth_price_samples": np.linspace(start=100, stop=3000, num=20),
    "eth_staked_samples": np.linspace(start=eth_staked, stop=min(eth_staked * 2, 33_600_000), num=20),
})

parameter_overrides = {
    "phase": [Phase.PHASE_0],
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
