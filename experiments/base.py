"""
The base experiment with default System Parameters, State Variables, and Simulation Configuration
"""

from radcad import Model, Simulation, Experiment, Engine

from model.system_parameters import parameters
from model.state_variables import initial_state
from model.state_update_blocks import state_update_blocks
from model.simulation_configuration import TIMESTEPS, DELTA_TIME, MONTE_CARLO_RUNS


# Create Model
model = Model(params=parameters, initial_state=initial_state, state_update_blocks=state_update_blocks)
# Create Model Simulation
simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=MONTE_CARLO_RUNS)
# Create Experiment of single Simulation
experiment = Experiment([simulation])
# Configure Experiment engine
experiment.engine = Engine(drop_substeps=True)
