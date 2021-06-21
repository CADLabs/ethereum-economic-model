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
#     display_name: Python (CADLabs Ethereum Model)
#     language: python
#     name: python-cadlabs-eth-model
# ---

# # State Space Analysis

# ## Setup

# Import the setup module, which runs shared notebook configuration methods, such as loading IPython modules:

import project_path
import notebooks.setup

# ## Dependencies

# Import notebook specific depependencies:

# +
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.io as pio

pd.options.plotting.backend = "plotly"
# -

from experiments.run import run
import experiments.notebooks.visualizations as visualizations

# ## Experiment

# Import the experiment to be run and analysed in this notebook:

from experiments.templates.state_space_analysis import experiment

# Run the experiment, and get the post-processed Pandas DataFrame:

df, _exceptions = run(experiment)

df

# ## Analysis

# Analyze and visualize the results:

# ### Ethereum System States

df.plot(x='timestamp', y='eth_price')

df = df.set_index('timestamp', drop=False)
fig = visualizations.plot_eth_supply_over_all_stages(df)
pio.write_image(fig, "../../outputs/eth_supply_stages.png", width=1080, height=720)
fig.show()

visualizations.plot_eth_supply_inflation_over_all_stages(df)

visualizations.plot_eth_staked_over_all_stages(df)

# ### Validator Rewards

# +
fig = df.plot(x='timestamp', y='total_online_validator_rewards_eth', title='Total Online Validator Rewards in ETH')

fig.update_layout(
    xaxis=dict(
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)

fig.show()
# -

# ### Validator Revenue and Profit

# +
fig = df.plot(x='timestamp', y=['total_revenue', 'total_profit'], title='Total Revenue and Profit')

fig.update_layout(
    xaxis=dict(
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)

fig.show()

# +
fig = df.plot(x='timestamp', y=['total_revenue_yields_pct', 'total_profit_yields_pct'], title='Annualized Revenue and Profit Yields')

fig.update_layout(
    xaxis=dict(
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)

fig.show()
# -

# ### Validator Costs

# +
df['total_costs_percentage_of_revenue'] = (df['total_network_costs'] / df['total_revenue']) * 100

fig = df.plot(x='timestamp', y='total_costs_percentage_of_revenue', title='Total Validator Costs as Percentage of Revenue')

fig.update_layout(
    xaxis=dict(
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)

fig.show()

# +
from model.system_parameters import validator_environments

hardware_costs = [validator.type + '_hardware_costs' for validator in validator_environments]
cloud_costs = [validator.type + '_cloud_costs' for validator in validator_environments]
third_party_costs = [validator.type + '_third_party_costs' for validator in validator_environments]
validator_costs = [validator.type + '_costs' for validator in validator_environments]

# +
fig = df.plot(x='timestamp', y=validator_costs, title='Validator Costs by Environment')

fig.update_layout(
    xaxis=dict(
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)

fig.show()
