import numpy as np

from experiments.default import experiment


parameter_overrides = {
    # Sweep of disabled and enabled EIP1559
    "eip1559_basefee": [0, 100],  # Gwei per gas
    "eip1559_avg_tip_amount": [0, 1],  # Gwei per gas
}

# Override default experiment parameters
experiment.simulations[0].model.params.update(parameter_overrides)
