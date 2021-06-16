import pandas as pd
import logging
import sys
from datetime import datetime

from experiments.default_experiment import experiment
from experiments.post_processing import post_process


# Configure logging framework
# e.g. Use logging.debug(...) to log to log file
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler(filename=f'logs/experiment-{datetime.now()}.log')
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def run(experiment=experiment):
  logging.info("Running experiment")
  experiment.run()
  logging.info("Experiment complete")

  logging.info("Post-processing results")
  df = pd.DataFrame(experiment.results)
  df = post_process(df)
  logging.info("Post-processing complete")

  return df, experiment.exceptions


if __name__ == '__main__':
  df, _exceptions = run()
  print(df)
