# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.10.3
#   kernelspec:
#     display_name: Python (Eth2)
#     language: python
#     name: python-eth2
# ---

# %% [markdown]
# # Justin Drake APR

# %%
import setup

# %%
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# %%
from experiments.run import run
import visualizations as visualizations
from model.parameters import parameters

# %%
from experiments.default import experiment, TIMESTEPS, DELTA_TIME

# %%
from model.types import Phase

# %%
daily_transactions = parameters["daily_transactions_process"][0]()
daily_transactions

# %%
transaction_average_gas = parameters["transaction_average_gas"][0]
transaction_average_gas

# %%
# Pre-process the basefee and tip process values from Justin Drake scenarios:
# https://docs.google.com/spreadsheets/d/1FslqTnECKvi7_l4x6lbyRhNtzW9f6CVEzwDf04zprfA

# Scenarios: optimistic, lean optimistic, best guess, lean conservative, conservative
eth_staked_scenarios = [4.5e6, 5e6, 6e6, 10e6, 15e6]
daily_evm_fees_scenarios = [15e3, 12e3, 10e3, 8e3, 6e3]
fee_burn_percentage_scenarios = [0.50, 0.60, 0.70, 0.75, 0.80]

basefee_values = []
tip_values = []

for scenario in range(len(eth_staked_scenarios)):
    basefee_pct = fee_burn_percentage_scenarios[scenario]
    tip_pct = 1 - basefee_pct
    evm_fees = daily_evm_fees_scenarios[scenario]
    
    basefee_plus_tip = (evm_fees * 1e9) / (daily_transactions * transaction_average_gas)
    basefee = basefee_plus_tip * basefee_pct
    tip = basefee_plus_tip * tip_pct
    
    basefee_values.append(basefee)
    tip_values.append(tip)
    
    print(daily_transactions * transaction_average_gas * (basefee + tip) / 1e9)

# %%
parameter_overrides = {
    "phase": [Phase.POST_MERGE],
    "eth_price_process": [lambda _run=None, _timestep=None: 3000],
    "eth_staked_process": [lambda _run=None, _timestep=None, eth_staked=eth_staked: eth_staked for eth_staked in eth_staked_scenarios],  # ETH
    "eip1559_basefee_process": [lambda _run=None, _timestep=None, basefee=basefee: basefee for basefee in basefee_values],  # Gwei per gas
    "eip1559_tip_process": [lambda _run=None, _timestep=None, tip=tip: tip for tip in tip_values],  # Gwei per gas
}

# Override default experiment parameters
experiment.simulations[0].model.params.update(parameter_overrides)
# Run single timestep, set unit of time to multiple epochs
experiment.simulations[0].timesteps = 1
experiment.simulations[0].model.params.update({"dt": [TIMESTEPS * DELTA_TIME]})

# %%
df, exceptions = run(experiment)

# %%
df

# %%
df['total_revenue_yields'] * 100

# %%
