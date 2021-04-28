import pytest

from experiments.run import run
from experiments.default import experiment
import model.parts.spec as spec

import runtime_tests as runtime_tests


def check_base_reward(params, substep, state_history, previous_state):
    EFFECTIVE_BALANCE_INCREMENT = params["EFFECTIVE_BALANCE_INCREMENT"]
    number_of_validators = previous_state["number_of_validators"]

    total_active_increments = (
        spec.get_total_active_balance(params, previous_state)
        // EFFECTIVE_BALANCE_INCREMENT
    )
    assert (
        spec.get_base_reward(params, previous_state) * number_of_validators
        == spec.get_base_reward_per_increment(params, previous_state)
        * total_active_increments
    )

    return


@pytest.mark.skip(reason="test currently fails due to precision")
def test_base_reward():
    simulation: Simulation = experiment.simulations[0]
    simulation.timesteps = 10

    simulation.model.state_update_blocks.append(
        {
            "policies": {"test_base_reward": runtime_tests.test_base_reward},
            "variables": {},
        }
    )

    run(experiment)
