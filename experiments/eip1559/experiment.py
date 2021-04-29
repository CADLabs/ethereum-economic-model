import numpy as np

from experiments.default import experiment


parameter_overrides = {
    # Sweep of EIP1559 disabled and enabled
    "eip1559_basefee_process": [lambda _run, _timestep: 0, lambda _run, _timestep: 100, lambda _run, _timestep: 70],  # Gwei per gas
    "eip1559_tip_process": [lambda _run, _timestep: 0, lambda _run, _timestep: 1, lambda _run, _timestep: 30],  # Gwei per gas
}

# Override default experiment parameters
experiment.simulations[0].model.params.update(parameter_overrides)
