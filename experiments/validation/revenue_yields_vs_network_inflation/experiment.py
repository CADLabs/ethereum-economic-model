import numpy as np

import model.simulation_configuration as simulation
from experiments.default import experiment


eth_staked_samples = np.linspace(
    524_288,  # From Hoban/Borgers Economic Report
    33_600_000,  # From Hoban/Borgers Economic Report
    simulation.TIMESTEPS * simulation.DELTA_TIME + 1
)

parameter_overrides = {
    "eth_staked_process": [
        lambda _run, timestep: eth_staked_samples[timestep],
    ],
    "eth_price_process": [
        # A sweep of two fixed ETH price points
        lambda _run, _timestep: 25,  # From Hoban/Borgers Economic Report
        lambda _run, _timestep: 1500,  # From Hoban/Borgers Economic Report
    ],
    # Combination of validator internet, power, and technical uptime from Hoban/Borgers Report
    "validator_uptime": [0.999 * 0.999 * 0.982],
    # Disable EIP1559
    "eip1559_basefee": [0],  # Gwei per gas
    "eip1559_avg_tip_amount": [0],  # Gwei per gas
}

# From Hoban/Borgers Economic Report
state_variable_overrides = {
    "eth_supply": 112_000_000,
    "eth_price": 25,
    "eth_staked": 524_288,
    "number_of_validators": 16_384,
}

# Override default experiment parameters
experiment.simulations[0].model.params.update(parameter_overrides)
# Override default experiment state variables
experiment.simulations[0].model.initial_state.update(state_variable_overrides)
