"""Experiment template example
An example of overriding and customizing the default experiment to create a new template.
"""

from experiments.default_experiment import experiment


parameter_overrides = {
    "dt": [1],
}

state_variable_overrides = {
    "eth_price": [0],
}

# Override default experiment System Parameters
experiment.simulations[0].model.params.update(parameter_overrides)
# Override default experiment Initial State
experiment.simulations[0].model.initial_state.update(state_variable_overrides)
