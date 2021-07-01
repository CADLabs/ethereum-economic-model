"""
The default experiment with default System Parameters, State Variables, and Simulation Configuration.

The defaults are defined in their respective modules (e.g. `model/system_parameters.py`).
"""

from radcad import Model, Simulation, Experiment, Backend

# Initialize RNG seed sequence for each experiment
from experiments.utils import rng_generator

seed = 1234
rng_generator(seed)

from model.system_parameters import parameters
from model.state_variables import initial_state
from model.state_update_blocks import state_update_blocks
from model.simulation_configuration import TIMESTEPS, MONTE_CARLO_RUNS


# Create Model
model = Model(params=parameters, initial_state=initial_state, state_update_blocks=state_update_blocks)
# Create Model Simulation
simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=MONTE_CARLO_RUNS)
# Create Experiment of single Simulation
experiment = Experiment([simulation])
# Configure Simulation & Experiment engine
simulation.engine = experiment.engine
experiment.engine.backend = Backend.SINGLE_PROCESS
experiment.engine.deepcopy = False
experiment.engine.drop_substeps = True
