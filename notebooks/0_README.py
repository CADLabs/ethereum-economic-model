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
# # Model Experiment Analysis Walk-through

# %% [markdown]
# The purpose of this notebook is to guide you interactively through how to configure the model and experiments, and introduce a couple of basic analyses - you can refer to the additional notebooks in this directory for further analyses, also referenced and described in the [README.md](../README.md).

# %% [markdown]
# ## Setup

# %% [markdown]
# Import the setup module, which runs shared notebook configuration methods, such as loading IPython modules:

# %%
import setup

# %% [markdown]
# ## Dependencies

# %% [markdown]
# Import notebook specific depependencies:

# %%
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from pprint import pprint

# Set Pandas plotting backend to use Plotly
pd.options.plotting.backend = "plotly"

# %%
from experiments.run import run
import visualizations as visualizations
import experiments as experiments

# %% [markdown]
# ## Experiment Configuration

# %% [markdown]
# To configure a custom experiment, we first import the default experiment configuration, and then override either the System Parameters, State Variables, or simulation configuration such as the number of timesteps.

# %%
visualizations.inspect_module(experiments.default)

# %% [markdown]
# The State Space experiment is an example of a custom experiment:

# %%
from experiments.state_space.experiment import experiment, parameter_overrides, DELTA_TIME, SIMULATION_TIME_MONTHS, TIMESTEPS

# %%
visualizations.inspect_module(experiments.state_space.experiment)

# %% [markdown]
# ### System Parameter Overrides

# %% [markdown]
# We use the `parameter_overrides` dictionary to override the default experiment configuration:
#
# ```python
# # Override default experiment System Parameters
# experiment.simulations[0].model.params.update(parameter_overrides)
# ```

# %%
parameter_overrides

# %% [markdown]
# ### Ethereum Network Upgrade Phases

# %% [markdown]
# We can see in the parameter overrides, that we're setting the simulation `Phase` to `Phase.ALL`. `Phase` is an Enum, we can import it and see what options we have:

# %%
from model.types import Phase

# %% [markdown]
# The model is well documented, and we can view the Python docstring to see what a Phase is, and create a dictionary to view the Enum members:

# %%
print(Phase.__doc__)
{e.name: e.value for e in Phase}

# %% [markdown]
# The `POST_MERGE` phase, for example, assumes EIP1559 has been enabled and POW issuance is disabled:

# %%
visualizations.inspect_module(Phase)

# %% [markdown]
# ### Simulation Timesteps and Unit of Time

# %% [markdown]
# We can configure the number of simulation timesteps `TIMESTEPS` from a simulation time in months `SIMULATION_TIME_MONTHS`, multiplied by the number of epochs in a month, and divided by the simulation unit of time `DELTA_TIME`:

# %%
SIMULATION_TIME_MONTHS / 12

# %% [markdown]
# ```python
# TIMESTEPS = constants.epochs_per_month * SIMULATION_TIME_MONTHS // DELTA_TIME
# ```

# %%
TIMESTEPS

# %% [markdown]
# And override the simulation timesteps (note, you may have to regenerate the environmental processes with the number of timesteps if changed, and override the relevant parameters):

# %%
experiment.simulations[0].timesteps = TIMESTEPS

# %% [markdown]
# ## Experiment Execution

# %% [markdown]
# We can now execute our custom experiment, and retrieve the post-processed Pandas DataFrame, using the `run(...)` method:

# %%
df, _exceptions = run(experiment)

# %%
df

# %% [markdown]
# ## Experiment Analysis

# %% [markdown]
# Once we have the results post-processed and in a Pandas DataFrame, we can use Plotly for plotting our results, or Pandas for numerical analyses.
#
# A couple of analyses from the State Space experiment have been included:

# %% [markdown]
# ### State Space
#
# An experiment that simulates the State Space of the model, with phases (Phase 0, EIP1559 enabled, The Merge) representing the upgrade process of the Eth2 system.
#
# * Notebook: [state_space.ipynb](state_space.ipynb)

# %%
df = df.set_index('timestamp', drop=False)
visualizations.plot_eth_supply_over_all_phases(df)

# %%
visualizations.plot_validating_rewards(df)
