from radcad import Model, Simulation, Experiment
import pandas as pd

from model.parameters import parameters
from model.state_variables import initial_state
from model.state_update_blocks import state_update_blocks


TIMESTEPS = 100
RUNS = 1

model = Model(params=parameters, initial_state=initial_state, state_update_blocks=state_update_blocks)
simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=RUNS)
experiment = Experiment([simulation])


def run(experiment=experiment):
  print("Running experiment")
  experiment.run()
  print("Experiment complete")

  return experiment.results, experiment.exceptions

if __name__ == '__main__':
  results, _exceptions = run()

  results_dataframe = pd.DataFrame(results)
  print(results_dataframe)
