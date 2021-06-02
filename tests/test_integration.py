import pytest
import math
from copy import deepcopy
import pandas as pd
from radcad import Simulation

import experiments.base as base


def test_dt():
    simulation: Simulation = deepcopy(base.experiment.simulations[0])

    simulation.timesteps = 1
    simulation.model.params.update({"dt": [1000]})

    results = simulation.run()
    df_timestep_1 = pd.DataFrame(results)

    simulation.timesteps = 1000
    simulation.model.params.update({"dt": [1]})

    results = simulation.run()
    df_timestep_1000 = pd.DataFrame(results)

    assert math.isclose(df_timestep_1.iloc[-1]["total_profit_yields"], df_timestep_1000.iloc[-1]["total_profit_yields"])
    assert math.isclose(df_timestep_1.iloc[-1]["total_online_validator_rewards"], df_timestep_1000.iloc[-1]["total_online_validator_rewards"] * 1000)


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
    simulation: Simulation = deepcopy(base.experiment.simulations[0])
    simulation.timesteps = 10

    simulation.model.params.update({
        'validator_uptime_process': [lambda _run, _timestep: 1.0],
    })

    simulation.model.state_update_blocks.append(
        {
            "policies": {"test_validating_rewards": check_validating_rewards},
            "variables": {},
        }
    )

    simulation.run()


def test_slashing():
    simulation: Simulation = deepcopy(base.experiment.simulations[0])
    simulation.timesteps = 10

    simulation.model.params.update({
        'dt': [1],
        'slashing_events_per_1000_epochs': [0],
    })

    results = simulation.run()
    df = pd.DataFrame(results)
    assert df['amount_slashed'].max() == 0

    simulation.model.params.update({
        'dt': [1],
        'slashing_events_per_1000_epochs': [1],
    })

    results = simulation.run()
    df = pd.DataFrame(results)
    assert df['amount_slashed'].max() == 500000.0


def test_eip1559_experiment():
    simulation: Simulation = deepcopy(base.experiment.simulations[0])
    simulation.timesteps = 10

    parameter_overrides = {
        # Sweep of EIP1559 disabled and enabled
        "eip1559_basefee_process": [
            lambda _run, _timestep: 0,
            lambda _run, _timestep: 100,
            lambda _run, _timestep: 70
        ],  # Gwei per gas
        "eip1559_tip_process": [
            lambda _run, _timestep: 0,
            lambda _run, _timestep: 1,
            lambda _run, _timestep: 30
        ],  # Gwei per gas
    }

    # Override default parameters
    simulation.model.params.update(parameter_overrides)

    results = simulation.run()
    df = pd.DataFrame(results)

    assert df.query("subset == 0")["total_tips_to_validators"].max() == 0
    assert df.query("subset == 1")["total_tips_to_validators"].max() != 0
