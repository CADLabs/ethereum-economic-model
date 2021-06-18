import pandas as pd
import logging
import sys
from datetime import datetime
import time

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

from experiments.templates.state_space_analysis import experiment
def run(experiment=experiment):
  logging.info("Running experiment")
  start_time = time.time()
  experiment.run()
  experiment_duration = time.time() - start_time
  logging.info(f"Experiment complete in {experiment_duration} seconds")

  logging.info("Post-processing results")
  df = pd.DataFrame(experiment.results)
  df = post_process(df)
  post_processing_duration = time.time() - start_time - experiment_duration
  logging.info(f"Post-processing complete in {post_processing_duration} seconds")

  return df, experiment.exceptions


if __name__ == '__main__':
  df, _exceptions = run()
  print(df)
