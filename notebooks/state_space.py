# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.10.3
#   kernelspec:
#     display_name: Python (Eth2)
#     language: python
#     name: python-eth2
# ---

# # Eth2 Validator Economics Model: State Space Experiment Analysis

# ## Setup

# Import the setup module, which runs shared notebook configuration methods, such as loading IPython modules:

import setup

# ## Dependencies

# Import notebook specific depependencies:

# +
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

pd.options.plotting.backend = "plotly"
# -

from experiments.run import run
from experiments.post_processing import post_process
import visualizations as visualizations

# ## Experiment

# Import the experiment to be run and analysed in this notebook:

from experiments.state_space.experiment import experiment

# Run the experiment, and get the raw results:

results, _exceptions = run(experiment)

# Convert the raw results to a Pandas DataFrame, and post-process the results:

df = pd.DataFrame(results)
df = post_process(df)
df

# ## Analysis

# Analyze and visualize the results:

df.plot(x='timestamp', y='eth_price')

# +
from model.parameters import parameters

df.reset_index(inplace=True)
df = df.set_index('timestamp')

date_start = parameters["date_start"][0]
date_eip1559 = parameters["date_eip1559"][0]
date_merge = parameters["date_merge"][0]
date_end = df.index[0]

fig = df.plot(y='eth_supply', title='ETH Supply', width=1000, height=600)

fig.add_shape(
    type="rect",
    xref="x",
    yref="paper",
    x0=date_start,
    y0=0,
    x1=date_eip1559,
    y1=1,
    line=dict(color="rgba(0,0,0,0)",width=3,),
    fillcolor="rgba(0,0,0,0.3)",
    layer='below'
)

fig.add_shape(
    type="rect",
    xref="x",
    yref="paper",
    x0=date_eip1559,
    y0=0,
    x1=date_merge,
    y1=1,
    line=dict(color="rgba(0,0,0,0)",width=3,),
    fillcolor="rgba(0,0,0,0.2)",
    layer='below'
)

fig.add_shape(
    type="rect",
    xref="x",
    yref="paper",
    x0=date_merge,
    y0=0,
    x1=date_end,
    y1=1,
    line=dict(color="rgba(0,0,0,0)",width=3,),
    fillcolor="rgba(0,0,0,0.1)",
    layer='below'
)

fig.add_annotation(
    x=date_eip1559, y=df.loc[date_eip1559.strftime("%Y-%m-%d")]['eth_supply'][0],
    text="EIP1559 Enabled",
    showarrow=True,
    arrowhead=1
)

fig.add_annotation(
    x=date_merge, y=df.loc[date_merge.strftime("%Y-%m-%d")]['eth_supply'][0],
    text="The Merge",
    showarrow=True,
    arrowhead=1,
)

df.reset_index(inplace=True)

fig.show()
# -

df.plot(x='timestamp', y='supply_inflation_pct')

df.plot(x='timestamp', y='total_online_validator_rewards_eth')

df.plot(x='timestamp', y='eth_staked')

visualizations.plot_validator_rewards(df)

# +
validator_rewards = df.iloc[-1][['source_reward_eth', 'target_reward_eth', 'head_reward_eth', 'block_proposer_reward_eth', 'sync_reward_eth']].to_dict()

px.pie(df, values=validator_rewards.values(), names=validator_rewards.keys(), title="Validator Rewards")

# +
validator_rewards = df.iloc[-1][['total_tips_to_validators_eth', 'source_reward_eth', 'target_reward_eth', 'head_reward_eth', 'block_proposer_reward_eth', 'sync_reward_eth']].to_dict()

px.pie(df, values=validator_rewards.values(), names=validator_rewards.keys(), title="Validator Rewards with tips")
# -

df.plot(x='timestamp', y=['total_revenue', 'total_network_costs'])

df.plot(x='timestamp', y=['total_revenue', 'total_profit'])

df.plot(x='timestamp', y=['total_revenue_yields_pct', 'total_profit_yields_pct'])

# +
from model.parameters import validator_types

hardware_costs = [validator.type + '_hardware_costs' for validator in validator_types]
cloud_costs = [validator.type + '_cloud_costs' for validator in validator_types]
third_party_costs = [validator.type + '_third_party_costs' for validator in validator_types]
# -

df.plot(x='timestamp', y=hardware_costs)

df.plot(x='timestamp', y=cloud_costs)

df.plot(x='timestamp', y=third_party_costs)


