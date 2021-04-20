import numpy as np

from experiments.default import experiment, TIMESTEPS, DELTA_TIME


# From Hoban/Borgers Economic Report
eth_price_samples = np.linspace(start=25, stop=1500, num=(TIMESTEPS * DELTA_TIME + 1))

parameter_overrides = {
    "eth_price_process": [
        lambda _run, timestep: eth_price_samples[timestep]
    ],
    "eth_staked_process": [
        lambda _run, _timestep: 524_288,  # From Hoban/Borgers Economic Report
        lambda _run, _timestep: 33_600_000,  # From Hoban/Borgers Economic Report
    ],
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
