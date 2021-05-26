from experiments.default import experiment


parameter_overrides = {
    # Sweep of EIP1559 disabled and enabled
    "eip1559_basefee_process": [
        lambda _run, _timestep: 0, # Disabled
        lambda _run, _timestep: 100, # Enabled: Steady state
        lambda _run, _timestep: 70 # Enabled: MEV scenario
    ],  # Gwei per gas
    "eip1559_tip_process": [
        lambda _run, _timestep: 0, # Disabled
        lambda _run, _timestep: 1, # Enabled: Steady state
        lambda _run, _timestep: 30 # Enabled: MEV scenario
    ],  # Gwei per gas
}

# Override default experiment parameters
experiment.simulations[0].model.params.update(parameter_overrides)
