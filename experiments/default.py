from radcad import Model, Simulation, Experiment, Engine

from model.parameters import parameters
from model.state_variables import initial_state
from model.state_update_blocks import state_update_blocks
from model.simulation_configuration import TIMESTEPS, DELTA_TIME, MONTE_CARLO_RUNS


model = Model(params=parameters, initial_state=initial_state, state_update_blocks=state_update_blocks)
simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=MONTE_CARLO_RUNS)
experiment = Experiment([simulation])
experiment.engine = Engine(drop_substeps=True)
