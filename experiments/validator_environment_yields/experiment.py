import numpy as np

from model.state_variables import eth_staked, eth_supply
from experiments.default import experiment, TIMESTEPS, DELTA_TIME
from model.types import Phase


# ETH price range from 100 $/ETH to 3000 $/ETH
eth_price_samples = np.linspace(start=100, stop=3000, num=(TIMESTEPS * DELTA_TIME + 1))

parameter_overrides = {
    "phase": [Phase.PHASE_0],
    "eth_price_process": [
        lambda _run, timestep: eth_price_samples[timestep]
    ],
    "eth_staked_process": [
        # A sweep of two fixed ETH staked points
        lambda _run, _timestep: eth_staked,  # From https://beaconscan.com/ as of 20/04/21
        lambda _run, _timestep: eth_supply * 0.3,  # 30% of current total ETH supply
    ],
}

# Override default experiment parameters
experiment.simulations[0].model.params.update(parameter_overrides)
