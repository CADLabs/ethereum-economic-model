import pytest

from experiments.run import run
from experiments.default import experiment
import model.parts.spec as spec

import runtime_tests as runtime_tests


@pytest.mark.skip(reason="test currently fails due to precision")
def test_base_reward():
    simulation: Simulation = experiment.simulations[0]
    simulation.timesteps = 10

    simulation.model.state_update_blocks.append({
        'policies': {
            'test_base_reward': runtime_tests.test_base_reward
        },
        'variables': {}
    })

    experiment.run()
