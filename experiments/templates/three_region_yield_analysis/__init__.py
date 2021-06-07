import numpy as np

from model.state_variables import eth_staked
from experiments.base import experiment, TIMESTEPS, DELTA_TIME
from model.types import Stage


# ETH price range from 100 $/ETH to 3000 $/ETH
eth_price_samples = np.linspace(start=100, stop=3000, num=50)

parameter_overrides = {
    "stage": [Stage.PHASE_0],
    "eth_price_process": [
        lambda run, _timestep: eth_price_samples[run - 1]
    ],
    "eth_staked_process": [
        # A sweep of two fixed ETH staked points
        lambda _run, _timestep: eth_staked,  # From https://beaconscan.com/ as of 20/04/21
    ],
}

# Override base experiment parameters
experiment.simulations[0].model.params.update(parameter_overrides)
# Set runs to number of combinations in sweep
experiment.simulations[0].runs = len(eth_price_samples)
# Run single timestep, set unit of time to multiple epochs
experiment.simulations[0].timesteps = 1
experiment.simulations[0].model.params.update({"dt": [TIMESTEPS * DELTA_TIME]})
