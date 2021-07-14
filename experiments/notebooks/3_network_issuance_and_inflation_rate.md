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

# Experiment Notebook: Network Issuance and Inflation Rate


# Table of Contents
* [Experiment Summary](#Experiment-Summary)
* [Experiment Assumptions](#Experiment-Assumptions)
* [Experiment Setup](#Experiment-Setup)
* [Analysis: Inflation Rate and ETH Supply Over Time](#Analysis:-Inflation-Rate-and-ETH-Supply-Over-Time)


# Experiment Summary 

The purpose of this notebook is to explore the ETH issuance and resulting annualized inflation rate across different time horizons, adoption scenarios, and network upgrade stages for both historical data and simulated states.

# Experiment Assumptions

See [assumptions document](../../ASSUMPTIONS.md) for further details.


# Experiment Setup

We begin with several experiment-notebook-level preparatory setup operations:

* Import relevant dependencies
* Import relevant experiment templates
* Create copies of experiments
* Configure and customize experiments 

Analysis-specific setup operations are handled in their respective notebook sections.

```html
<style>
.python-iframe > iframe {
  max-height:1000px !important;
}
</style>
```

```python tags=[]
import setup

import copy
import logging
import IPython
import numpy as np
import pandas as pd
from datetime import datetime

import experiments.notebooks.visualizations as visualizations
from experiments.notebooks.visualizations.peak_eth_simulator import run_peak_eth_simulator
from experiments.run import run
from model.types import Stage
from data.historical_values import df_ether_supply
```

```python
# Enable/disable logging
logger = logging.getLogger()
logger.disabled = False
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
```

```python
# Import experiment templates
import experiments.templates.time_domain_analysis as time_domain_analysis
```

```python
# Fetch the time-domain analysis experiment
experiment = time_domain_analysis.experiment
# Create a copy of the experiment simulation
simulation = copy.deepcopy(experiment.simulations[0])
```

```python
# Experiment configuration

simulation_names = {
    'Validator Adoption Scenarios': [
        'Normal Adoption',
        'Low Adoption',
        'High Adoption'
    ],
    'PoS Activation Date Scenarios': [
        "2021/12/1",
        "2022/03/1",
        "2022/06/1",
    ],
    'EIP1559 Scenarios': [
        'Disabled',
        'Enabled: Steady State',
        'Enabled: MEV',
    ]
}

simulation_1 = copy.deepcopy(simulation)
simulation_1.model.params.update({
    'validator_process': [
        lambda _run, _timestep: 3,  # Normal adoption: current average active validators per-epoch from Beaconscan
        lambda _run, _timestep: 3 * 0.5,  # Low adoption: 50% lower scenario
        lambda _run, _timestep: 3 * 1.5,  # High adoption: 50% higher scenario
    ],
})

simulation_2 = copy.deepcopy(simulation)
simulation_2.model.params.update({
    'date_pos': [
        datetime.strptime("2021/12/1", "%Y/%m/%d"),
        datetime.strptime("2022/03/1", "%Y/%m/%d"),
        datetime.strptime("2022/06/1", "%Y/%m/%d"),
    ],
})

simulation_3 = copy.deepcopy(simulation)
simulation_3.model.params.update({
    'base_fee_process': [
        lambda _run, _timestep: 0, # Disabled
        lambda _run, _timestep: 100, # Enabled: Steady state
        lambda _run, _timestep: 70, # Enabled: MEV
    ],  # Gwei per gas
    'priority_fee_process': [
        lambda _run, _timestep: 0, # Disabled
        lambda _run, _timestep: 1, # Enabled: Steady state
        lambda _run, _timestep: 30, # Enabled: MEV
    ],  # Gwei per gas
})

experiment.simulations = [
    simulation_1,
    simulation_2,
    simulation_3
]
```

```python
df, _exceptions = run(experiment)
```

# Analysis: Inflation Rate and ETH Supply Over Time

This analysis enables the exploration of inflation rate and ETH supply over time, and supports the three adoption scenarios introduced in the second experiment notebook, as well as custom parameter choices for the Proof-of-Stake (PoS) Activation Date ("The Merge") and EIP1559 base fee and average priority fee.

Default scenarios were selected for each of the Validator Adoption, Proof-of-Stake Activation Date, and EIP1559 categories:
* Validator Adoption (from experiment notebook two)
    * Normal adoption: current average active validators per-epoch from Beaconscan
    * Low adoption: 50% lower scenario
    * High adoption: 50% higher scenario
* Proof-of-Stake Activation Date
    * Various dates starting from the expected activation date of the 1st of Decemeber 2021 in quarterly increments
* EIP1559 Base Fee and Average Priority Fee (Gwei per gas)
    * base fee = 0 and priority fee = 0 to indicate EIP1559 being disabled
    * base fee = 100 and priority fee = 1 to indicate the expected steady state at current gas prices
    * base fee = 70 and tip = 30 to indicate the expected influence of MEV on the resulting blockspace auction

The first chart ("Inflation Rate and ETH Supply Analysis Scenarios") visualizes the ETH supply for default scenarios of the Validator Adoption, Proof-of-Stake Activation Date, and EIP1559 scenario categories, side-by-side (choose via button selector). This allows comparative analysis for each category.

We can interpret that:
* Increased Validator Adoption (i.e. implied ETH staked over time) results in higher inflation, due to increased issuance for validator rewards
* A delay in the Proof-of-Stake Activation Date results in a higher peak ETH supply, due to Proof-of-Work issuance being significantly higher than that of Proof-of-Stake
* EIP1559 results in a deflationary ETH supply, and MEV lowers the base fee in proportion to the increase in priority fee, which reduces the ETH burned and in turn increases the annual inflation rate

The second chart ("Inflation Rate and ETH Supply Over Time") visualizes the historical inflation rate and ETH supply over time alongside the simulated projections of the inflation rate and ETH supply. Various historical and simulated milestones are included for context - such as the "Homestead" hard-fork causing a temporary increase in the inflation rate, or the simulated effect of EIP1559 being enabled and Proof-of-Stake being activated. The interface allows us to both select the default scenarios defined above, or customize each parameter for unique analyses.

```python
visualizations.plot_network_issuance_scenarios(df, simulation_names)
```

```python
logger.disabled = True

# This will either display in "inline" mode when using Jupyter Notebook,
# or "jupyterlab" mode when using Jupyter Lab
run_peak_eth_simulator()
```
