import pytest
from copy import deepcopy
import time
import pandas as pd
from pandas._testing import assert_frame_equal
from radcad import Simulation

import experiments.templates.time_domain_analysis as time_domain_analysis


def test_deepcopy():
    simulation_1: Simulation = deepcopy(time_domain_analysis.experiment.simulations[0])
    simulation_2: Simulation = deepcopy(time_domain_analysis.experiment.simulations[0])

    exec_time_1 = time.time()
    simulation_1.engine.deepcopy = True
    df_1 = pd.DataFrame(simulation_1.run())
    exec_time_1 = time.time() - exec_time_1

    exec_time_2 = time.time()
    simulation_2.engine.deepcopy = False
    df_2 = pd.DataFrame(simulation_2.run())
    exec_time_2 = time.time() - exec_time_2

    assert exec_time_1 > exec_time_2
    assert_frame_equal(df_1, df_2)
