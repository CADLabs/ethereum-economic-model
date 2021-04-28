import pytest
import math

from experiments.run import run
from experiments.default import experiment


def check_validating_rewards(params, substep, state_history, previous_state):
    # State Variables
    validating_rewards = previous_state["validating_rewards"]
    block_proposer_reward = previous_state["block_proposer_reward"]
    sync_reward = previous_state["sync_reward"]
    source_reward = previous_state["source_reward"]
    target_reward = previous_state["target_reward"]
    head_reward = previous_state["head_reward"]

    # Assert sync reward is 1/8 of validating rewards
    assert math.isclose(sync_reward, (1 / 8) * validating_rewards)
    # Assert block proposer reward is 1/8 of validating rewards
    assert math.isclose(block_proposer_reward, (1 / 8) * validating_rewards)
    # Assert source reward is 3/4 of validating rewards
    assert math.isclose(source_reward + target_reward + head_reward, (3 / 4) * validating_rewards)
    
    return


def test_validating_rewards():
    simulation: Simulation = experiment.simulations[0]
    simulation.timesteps = 10

    simulation.model.params.update({
        'validator_internet_uptime': [1.0],
        'validator_power_uptime': [1.0],
        'validator_technical_uptime': [1.0],
    })

    simulation.model.state_update_blocks.append(
        {
            "policies": {"test_validating_rewards": check_validating_rewards},
            "variables": {},
        }
    )

    run(experiment)
