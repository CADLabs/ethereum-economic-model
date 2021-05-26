import numpy as np

from model.simulation_configuration import TIMESTEPS, DELTA_TIME
from model.state_variables import eth_staked, eth_supply
from experiments.default import experiment
from model.types import Phase


eth_staked_samples = np.linspace(
    eth_staked,  # From https://beaconscan.com/ as of 20/04/21
    eth_supply * 0.3,  # 30% of current total ETH supply
    TIMESTEPS * DELTA_TIME + 1
)

parameter_overrides = {
    "phase": [Phase.PHASE_0],
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
