"""Experiment template example
An example of overriding and customizing the base experiment to create a new template.
"""

from experiments.base import experiment


parameter_overrides = {
    "dt": [1],
}

state_variable_overrides = {
    "eth_price": [0],
}

# Override base experiment System Parameters
experiment.simulations[0].model.params.update(parameter_overrides)
# Override base experiment Initial State
experiment.simulations[0].model.initial_state.update(state_variable_overrides)
