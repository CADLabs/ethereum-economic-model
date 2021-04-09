from experiments.default import experiment


parameter_overrides = {
    "eth_price_process": [
        lambda _run, _timestep: 25,
        lambda _run, _timestep: 1500,
    ]
}

# Override default experiment parameters
experiment.simulations[0].model.params.update(parameter_overrides)
