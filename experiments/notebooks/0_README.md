---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.10.3
  kernelspec:
    display_name: Python (CADLabs Ethereum Model)
    language: python
    name: python-cadlabs-eth-model
---

# Experiment Quick-Start Guide


## Table of Contents

* [Overview of experiment architecture](#Overview-of-experiment-architecture)
* [Experiment workflow](#Experiment-workflow)
    * [Modifying State Variables](#Modifying-State-Variables)
    * [Modifying System Parameters](#Modifying-System-Parameters)
    * [Executing experiments](#Executing-experiments)
    * [Post-processing and analysing results](#Post-processing-and-analysing-results)
    * [Visualizing results](#Visualizing-results)
* [Creating new, customized experiment notebooks](#Creating-new,-customized-experiment-notebooks)
    * Step 1: Select an experiment template
    * Step 2: Create a new notebook
    * Step 3: Customize the experiment
    * Step 4: Execute the experiment
* [Advanced experiment configuration & simulation techniques](#Advanced-experiment-configuration-&-simulation-techniques)
    * [Setting simulation timesteps and unit of time `dt`](#Setting-simulation-timesteps-and-unit-of-time-dt)
    * [Changing the Ethereum network upgrade stage](#Changing-the-Ethereum-network-upgrade-stage)
    * [Performing large-scale experiments](#Performing-large-scale-experiments)


# Overview of experiment architecture

The experiment architecture is composed of the following four elements - the **model**, **default experiment**, **experiment templates**, and **experiment notebooks**:

1. The **model** is initialized with a default Initial State and set of System Parameters defined in the `model` module.
2. The **default experiment**, in the `experiments.default_experiment` module, is an experiment composed of a single simulation that uses the default cadCAD **model** Initial State and System Parameters. Additional default simulation execution settings such as the number of timesteps and runs are also set in the **default experiment**.
3. The **experiment templates**, in the `experiments.templates` module, contain pre-configured analyses based on the **default experiment**. Examples include `experiments.templates.time_domain_analysis` (simulation in the time-domain over a period of 5 years) and `experiments.templates.eth_price_sweep_analysis` (simulation in the phase-space sweeping over discrete ETH Price values).
4. The **experiment notebooks** perform various scenario analyses by importing existing **experiment templates**, optionally modifying the Initial State and System Parameters within the notebook, and then executing them.


# Experiment workflow

If you just want to run (execute) existing experiment notebooks, simply open the respective notebook and execute all cells.


The experiment notebooks will start by importing some standard dependencies:

```python
# Import the setup module:
# * sets up the Python path
# * runs shared notebook configuration methods, such as loading IPython modules
import setup

# External dependencies
import copy
import logging
import numpy as np
from pprint import pprint
import pandas as pd

# Project dependencies
import model.constants as constants
import experiments.notebooks.visualizations as visualizations
from experiments.run import run
from experiments.utils import inspect_module
```

We can then import the default experiment, and create a copy of the simulation object - we create a new copy for each analysis we'd like to perform:

```python
import experiments.default_experiment as default_experiment
import experiments.templates.time_domain_analysis as time_domain_analysis
import experiments.templates.eth_price_eth_staked_grid_analysis as eth_price_eth_staked_grid_analysis

simulation_analysis_1 = copy.deepcopy(default_experiment.experiment.simulations[0])
simulation_analysis_2 = copy.deepcopy(time_domain_analysis.experiment.simulations[0])
simulation_analysis_3 = copy.deepcopy(eth_price_eth_staked_grid_analysis.experiment.simulations[0])
```

We can use the `inspect_module` method to see the configuration of the default experiment before making changes:

```python
inspect_module(default_experiment)
```

## Modifying State Variables


To view what the Initial State (radCAD model configuration setting `initial_state`) of the State Variables are, and to what value they have been set, we can inspect the dictionary as follows:

```python
pprint(simulation_analysis_1.model.initial_state)
```

To modify the value of **State Variables** for a specific analysis you need to select the relevant simulation, and update the chosen model Initial State. For example, updating the `eth_supply` Initial State to `100e6` (100 million ETH):

```python
simulation_analysis_1.model.initial_state.update({
    "eth_supply": 100e6, 
})
```

## Modifying System Parameters


To view what the System Parameters (radCAD model configuration setting `params`) are, and to what value they have been set, we can inspect the dictionary as follows:

```python
pprint(simulation_analysis_1.model.params)
```

To modify the value of **System Parameters** for a specific analysis you need to select the relevant simulation, and update the chosen model System Parameter (which is a list of values). For example, updating the `BASE_REWARD_FACTOR` System Parameter to a sweep of two values, `64` and `32`:

```python
simulation_analysis_1.model.params.update({
    "BASE_REWARD_FACTOR": [64, 32],
})
```

## Executing experiments


We can now execute our custom analysis, and retrieve the post-processed Pandas DataFrame, using the `run(...)` method:

```python
df, exceptions = run(simulation_analysis_1)
```

## Post-processing and analysing results


We can see that we had no exceptions for the single simulation we executed:

```python
exceptions[0]['exception'] == None
```

We can simply display the Pandas DataFrame to inspect the results. This DataFrame already has some default post-processing applied (see [experiments/post_processing.py](../post_processing.py))

```python
df
```

## Visualizing results


Once we have the results post-processed and in a Pandas DataFrame, we can use Plotly for plotting our results, or Pandas for numerical analyses:

```python
visualizations.plot_validating_rewards(df, subplot_titles=["Base Reward Factor = 64", "Base Reward Factor = 32"])
```

# Creating new, customized experiment notebooks

If you want to create an entirely new analysis you'll need to create a new experiment notebook, which entails the following steps:
* Step 1: Select a base experiment template from the `experiments/templates/` directory to start from. The template [example_analysis.py](../templates/example_analysis.py) gives an example of extending the default experiment to override default State Variables and System Parameters.
* Step 2: Create a new notebook in the `experiments/notebooks/` directory, using the [template.ipynb](./template.ipynb) notebook as a guide, and import the experiment from the experiment template.
* Step 3: Customize the experiment for your specific analysis.
* Step 4: Execute your experiment, post-process and analyze the results, and create Plotly charts!


# Advanced experiment configuration & simulation techniques


## Setting simulation timesteps and unit of time `dt`

```python
from model.simulation_configuration import TIMESTEPS, DELTA_TIME, SIMULATION_TIME_MONTHS
```

We can configure the number of simulation timesteps `TIMESTEPS` from a simulation time in months `SIMULATION_TIME_MONTHS`, multiplied by the number of epochs in a month, and divided by the simulation unit of time `DELTA_TIME`:

```python
SIMULATION_TIME_MONTHS / 12  # Divide months by 12 to get number of years
```

`DELTA_TIME` is a variable that sets how many epochs are simulated for each timestep. Sometimes if we don't need a finer granularity (1 epoch per timestep, for example), then we can set `DELTA_TIME` to a larger value for better performance. The default value is 1 day or `225` epochs. This means that all our time based states will be for a period of 1 day (we call this "aggregation"), which is convenient.

```python
DELTA_TIME
```

`TIMESTEPS` is now simply the simulation time in months, multiplied by the number of epochs in a month, divided by `DELTA_TIME`:

<!-- #region -->
```python
TIMESTEPS = constants.epochs_per_month * SIMULATION_TIME_MONTHS // DELTA_TIME
```
<!-- #endregion -->

```python
TIMESTEPS
```

Finally, to set the simulation timesteps (note, you may have to update the environmental processes that depend on the number of timesteps, and override the relevant parameters):

```python
simulation_analysis_1.timesteps = TIMESTEPS
```

### Considerations when performing efficient phase-space simulations


In `simulation_analysis_3`, `timesteps` is decreased to `1`, but `dt` is increased to `TIMESTEPS * DELTA_TIME`, where `DELATA_TIME` is the full duration of the simulation. This produces the final result in a single processing cycle, producing the full phase-space with very low processing overhead. This is achieved by ignoring all time-series information between the beginning and end of the simulation.

There is a test function `test_dt(...)` in `tests/test_integration.py` that can be used to verify no information is lost due to the approximations taken along the time axis for the specific State Variables that you are interested in, and that your custom code has not introduced mechanisms that might not work well with this kind of approximation. 

An example of a type of mechanism that would not work with this kind of approximation is a mechanism that implements some form of feedback loop.


## Changing the Ethereum network upgrade stage


The model operates over different Ethereum network upgrade stages. The default experiment operates in the "post-merge" Proof of Stake stage.

`Stage` is an Enum, we can import it and see what options we have:

```python
from model.types import Stage
```

The model is well documented, and we can view the Python docstring to see what a Stage is, and create a dictionary to view the Enum members:

```python
print(Stage.__doc__)
{e.name: e.value for e in Stage}
```

The `PROOF_OF_STAKE` stage, for example, assumes the Beacon Chain has been implemented, EIP1559 has been enabled, and POW issuance is disabled:

```python
inspect_module(Stage)
```

As before, we can update the "stage" System Parameter to set the relevant Stage:

```python
simulation_analysis_1.model.params.update({
    "stage": [Stage.PROOF_OF_STAKE]
})
```

## Performing large-scale experiments


When executing an experiment, we have three degrees of freedom - **simulations, runs, and subsets** (parameter sweeps).

For a single experiment we can have multiple simulations, for every simulation we can have multiple runs, and for every run we can have multiple subsets. Remember that `simulation`, `run`, and `subset` are simply additional State Variables set by the radCAD engine during execution - we then use those State Variables to index the results for a specific dimension e.g. simulation 1, run 5, and subset 2.

Each dimension has a generally accepted purpose:
* Simulations are used for A/B testing
* Runs are used for Monte Carlo analysis
* Subsets are used for parameter sweeps

In some cases, we break these "rules" to allow for more degrees of freedom or easier configuration.

An example of this, is the `eth_price_eth_staked_grid_analysis` experiment template that we imported earlier:

```python
inspect_module(eth_price_eth_staked_grid_analysis)
```

Here, we create a grid of two State Variables, ETH price and ETH staked, using the `eth_price_process` and `eth_staked_process`.

Instead of sweeping the two System Parameters to create different subsets, we pre-generate all possible combinations of the two values first and use the specific `run` to index the data i.e. for each run we get a new ETH price and ETH staked sample.

This allows the experimenter (you!) to use a parameter sweep on top of this analysis if they choose, we have kept one degree of freedom.


### Composing an experiment using **simulations, runs, and subsets**

```python
from radcad import Experiment, Engine, Backend


# Create a new Experiment of three Simulations:
# * Simulation Analysis 1 has one run and two subsets - a parameter sweep of two values (BASE_REWARD_FACTOR = [64, 32])
# * Simulation Analysis 2 has one run and one subset - a basic simulation configuration
# * Simulation Analysis 3 has 400 runs (20 * 20) and one subset - a parameter grid indexed using `run`
experiment = Experiment([simulation_analysis_1, simulation_analysis_2, simulation_analysis_3])
```

### Configuring the radCAD Engine for high performance

To improve simulation performance for large-scale experiments, we can set the following settings using the radCAD `Engine` - both Experiments and Simulations have the same `Engine`, when executing an `Experiment` we set these settings on the `Experiment` instance:

```python
# Configure Experiment Engine
experiment.engine = Engine(
    # Use a single process, the overhead of creating multiple processes
    # for parallel-processing is only worthwhile when the Simulation runtime is long
    backend = Backend.SINGLE_PROCESS,
    # Disable System Parameter and State Variable deepcopy:
    # * Deepcopy prevents mutation of state, at the cost of lower performance
    # * Disabling it leaves it up to the experimenter to use Python best-practises to avoid 
    # state mutation, like manually using `copy` and `deepcopy` methods before
    # performing mutating calculations when necessary
    deepcopy = False,
    # If we don't need the state history from individual substeps,
    # we can get rid of them for higher performance
    drop_substeps = True,
)

# Disable logging
# For large experiments, there is lots of logging which can get messy...
logger = logging.getLogger()
logger.disabled = True

# Execute Experiment
raw_results = experiment.run()
```

### Indexing a large-scale experiment dataset

```python
# Create a Pandas DataFrame from the raw results
df = pd.DataFrame(experiment.results)
df
```

```python
# Select each Simulation dataset
df_0 = df[df.simulation == 0]
df_1 = df[df.simulation == 1]
df_2 = df[df.simulation == 2]

datasets = [df_0, df_1, df_2]

# Determine size of Simulation datasets
for index, data in enumerate(datasets):
    runs = len(data.run.unique())
    subsets = len(data.subset.unique())
    timesteps = len(data.timestep.unique())
    
    print(f"Simulation {index} has {runs} runs * {subsets} subsets * {timesteps} timesteps = {runs * subsets * timesteps} rows")
```

```python
# Indexing simulation 0, run 1 (indexed from one!), subset 1, timestep 1
df.query("simulation == 0 and run == 1 and subset == 1 and timestep == 1")
```
