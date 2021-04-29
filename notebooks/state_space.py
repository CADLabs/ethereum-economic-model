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

pd.options.plotting.backend = "plotly"
# -

from experiments.run import run
from experiments.post_processing import post_process
import visualizations as visualizations

# ## Experiment

# Import the experiment to be run and analysed in this notebook:

from experiments.default import experiment

# Run the experiment, and get the raw results:

results, _exceptions = run(experiment)

# Convert the raw results to a Pandas DataFrame, and post-process the results:

df = pd.DataFrame(results)
df = post_process(df)
df

# ## Analysis

# Analyze and visualize the results:

df.plot(x='timestamp', y='eth_price')

df.plot(x='timestamp', y='eth_supply')

df.plot(x='timestamp', y='supply_inflation_pct')

df.plot(x='timestamp', y='eth_staked')

df.plot(x='timestamp', y=['number_of_validators_in_activation_queue','number_of_validators'])

fig = visualizations.plot_validator_rewards(df)
fig.show()
fig.write_image("../outputs/validator_rewards.png")

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


