import pandas as pd

from experiments.default import experiment


def run(experiment=experiment):
  print("Running experiment")
  experiment.run()
  print("Experiment complete")

  return experiment.results, experiment.exceptions

if __name__ == '__main__':
  results, _exceptions = run()

  results_dataframe = pd.DataFrame(results)
  print(results_dataframe)
