import os
import pandas as pd
from celery import Celery
from radcad import Backend

from experiments import default_experiment
from experiments.run import run


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


@celery.task(name="experiment")
def create_task(task_type):
    experiment = default_experiment.experiment
    experiment.engine.backend = Backend.SINGLE_PROCESS
    experiment.engine.deepcopy = False
    experiment.engine.drop_substeps = True

    raw_result = run(experiment)
    json_response = pd.DataFrame(raw_result).to_json()

    return json_response
