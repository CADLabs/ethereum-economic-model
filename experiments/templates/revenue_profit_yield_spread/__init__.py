import numpy as np

from model.state_variables import eth_staked, eth_supply
from experiments.base import experiment, TIMESTEPS, DELTA_TIME
from experiments.utils import generate_cartesian_product
from model.types import Stage


sweep = generate_cartesian_product({
    # ETH price range from 100 $/ETH to 3000 $/ETH
    "eth_price_samples": np.linspace(start=100, stop=3000, num=20),
    # ETH staked range from genesis requirement to current ETH staked
    "eth_staked_samples": np.linspace(start=524_288, stop=eth_staked, num=20),
})

parameter_overrides = {
    "stage": [Stage.BEACON_CHAIN],
    "eth_price_process": [
        lambda run, _timestep: sweep["eth_price_samples"][run - 1]
    ],
    "eth_staked_process": [
        lambda run, _timestep: sweep["eth_staked_samples"][run - 1]
    ]
}

# Override base experiment parameters
experiment.simulations[0].model.params.update(parameter_overrides)
# Set runs to number of combinations in sweep
experiment.simulations[0].runs = len(sweep["eth_price_samples"])
# Run single timestep, set unit of time to multiple epochs
experiment.simulations[0].timesteps = 1
experiment.simulations[0].model.params.update({"dt": [TIMESTEPS * DELTA_TIME]})
