"""
# Time Domain Analysis

Executes a time-domain simulation over a long time period of 5 years,
over all Ethereum network upgrade stages.
"""

import copy
import pandas as pd

import model.constants as constants
from model.stochastic_processes import create_stochastic_process_realizations
from model.types import Stage
from experiments.default_experiment import experiment
from data.historical_values import df_ether_supply


# Make a copy of the default experiment to avoid mutation
experiment = copy.deepcopy(experiment)

DELTA_TIME = constants.epochs_per_day  # epochs per timestep
SIMULATION_TIME_MONTHS = 12 * 5  # number of months
TIMESTEPS = constants.epochs_per_month * SIMULATION_TIME_MONTHS // DELTA_TIME

# Generate stochastic process realizations
eth_price_samples = create_stochastic_process_realizations("eth_price_samples", timesteps=TIMESTEPS, dt=DELTA_TIME)

# Get mean daily PoW issuance over the 6 months pre-EIP1559
params = experiment.simulations[0].model.params
date_eip1559 = params['date_eip1559'][0]
df_ether_supply = df_ether_supply.resample('D').pad()
df_ether_supply['eth_supply_daily_issuance'] = (
        df_ether_supply['eth_supply'] - df_ether_supply['eth_supply'].shift(1)
)
average_daily_pow_issuance = df_ether_supply['eth_supply_daily_issuance'].loc[
    (date_eip1559 - pd.DateOffset(months=6)):date_eip1559
].mean()

# Create parameter override dictionary
parameter_overrides = {
    "stage": [Stage.ALL],
    "eth_price_process": [
        lambda run, timestep: eth_price_samples[run - 1][timestep]
    ],
    "daily_pow_issuance": [
        average_daily_pow_issuance
    ]  # 12_300
}

initial_state_overrides = {
    "eth_supply": df_ether_supply['eth_supply'].iloc[-1],
}

# Override default experiment Simulation and System Parameters related to timing
experiment.simulations[0].timesteps = TIMESTEPS
experiment.simulations[0].model.params.update({"dt": [DELTA_TIME]})

# Override default experiment System Parameters
experiment.simulations[0].model.params.update(parameter_overrides)

# Override default experiment Initial State
experiment.simulations[0].model.initial_state.update(initial_state_overrides)
