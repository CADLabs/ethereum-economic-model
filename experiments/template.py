"""Experiment template
A template to override and customize the default experiment. 
"""

from experiments.default import experiment


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
