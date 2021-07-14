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

# Experiment Notebook: Validator Revenue and Profit Yields


# Table of Contents
* [Experiment Summary](#Experiment-Summary)
* [Experiment Assumptions](#Experiment-Assumptions)
* [Experiment Setup](#Experiment-Setup)
* [Analysis 1: Revenue and Profit Yields Over Time](#Analysis-1:-Revenue-and-Profit-Yields-Over-Time)
* [Analysis 2: Revenue and Profit Yields Over ETH Staked](#Analysis-2:-Revenue-and-Profit-Yields-Over-ETH-Staked)
* [Analysis 3: Revenue and Profit Yields Over ETH Price](#Analysis-3:-Revenue-and-Profit-Yields-Over-ETH-Price)
* [Analysis 4: Profit Yields Over ETH Staked vs. ETH Price (Yield Surface)](#Analysis-4:-Profit-Yields-Over-ETH-Staked-vs.-ETH-Price)
* [Analysis 5: Profit Yields By Validator Environment Over Time](#Analysis-5:-Profit-Yields-By-Validator-Environment-Over-Time)


# Experiment Summary 

The purpose of this notebook is to explore the returns validators can expect from staking in the Ethereum protocol across different time horizons, adoption scenarios, ETH price scenarios, and validator environments.

# Experiment Assumptions

See [assumptions document](../../ASSUMPTIONS.md) for further details.


# Experiment Setup

We begin with several experiment-notebook-level preparatory setup operations:

* Import relevant dependencies
* Import relevant experiment templates
* Create copies of experiments
* Configure and customize experiments 

Analysis-specific setup operations are handled in their respective notebook sections.

```python
import setup

import copy
import logging
import numpy as np
import pandas as pd

import experiments.notebooks.visualizations as visualizations
import model.constants as constants
from experiments.run import run
from experiments.utils import inspect_module
from model.types import Stage
from model.system_parameters import validator_environments
from model.state_variables import eth_staked, eth_supply
```

```python
# Enable/disable logging
logger = logging.getLogger()
logger.disabled = True
```

```python
# Import experiment templates
import experiments.templates.time_domain_analysis as time_domain_analysis
import experiments.templates.eth_staked_sweep_analysis as eth_staked_sweep_analysis
import experiments.templates.eth_price_sweep_analysis as eth_price_sweep_analysis
import experiments.templates.eth_price_eth_staked_grid_analysis as eth_price_eth_staked_grid_analysis
```

```python
# Create a new copy of the relevant simulation for each analysis
simulation_1 = copy.deepcopy(time_domain_analysis.experiment.simulations[0])
simulation_2 = copy.deepcopy(eth_staked_sweep_analysis.experiment.simulations[0])
simulation_3 = copy.deepcopy(eth_price_sweep_analysis.experiment.simulations[0])
simulation_4 = copy.deepcopy(eth_price_eth_staked_grid_analysis.experiment.simulations[0])
simulation_5 = copy.deepcopy(time_domain_analysis.experiment.simulations[0])
```

# Analysis 1: Revenue and Profit Yields Over Time

This analysis allows the exploration of revenue and profit yields over time, and across three adoption scenarios:

* Normal adoption: assumes the current average of 3 new validators per-epoch from Beaconscan over the last 6 months
* Low adoption: assumes a 50% lower than average scenario
* High adoption: assumes a 50% higher than average scenario

The first chart ("Validator Adoption Scenarios") visualizes the three adoption scenarios (i.e. implied ETH staked over time) underlying Analysis 1. Please note that the High Adoption Scenario has non-linear dynamics due to the validator activation queue rate limiting. To create custom adoption scenarios, add another entry to the `validator_process` System Parameter, with either a static per-epoch validator adoption rate, or generate a time-series using the current timestep to index the data.

The second chart ("Revenue and Profit Yields Over Time - At a Glance") visualizes both revenue and profit yields over time and across the three adoption scenarios (i.e. implied ETH staked over time). The ETH price (relevant for profit yields) is by default set to the mean ETH price over the last 12 months. The higher the adoption, the lower both revenue and profit yields. The higher the ETH price, the higher the profit yields - whereas validator operational costs are fixed in dollars, returns are in ETH and their equivalent dollar value depends on the current ETH price.

The third chart ("Revenue or Profit Yields Over Time") visualizes revenue yields or profit yields (choose using button selector) over the chosen time frame, and across the three adoption scenarios  (i.e. implied ETH staked over time) and ETH price range. In simple terms, this chart visualizes how validators can expect the yield dynamics to change over different adoption and price scenarios. The higher the adoption, the lower both revenue and profit yields. The higher the price, the higher the profit yields.

The fourth chart ("Cumulative Average Revenue or Profit Yields Over Time") visualizes the cumulative average revenue yields or profit yields (choose via button selector) over the chosen time frame, and across the three adoption scenarios (i.e. implied ETH staked over time) and ETH price range. In simple terms, this chart visualizes the effective yields a validator can expect over the respective time horizons if they start validating today. The higher the adoption, the lower both revenue and profit yields. The higher the price, the higher the profit yields.

```python
simulation_1.model.params.update({
    'stage': [Stage.BEACON_CHAIN],
    'validator_process': [
        lambda _run, _timestep: 3,  # Normal adoption: current average active validators per epoch from Beaconscan
        lambda _run, _timestep: 3 * 0.5,  # Low adoption: 50% lower scenario
        lambda _run, _timestep: 3 * 1.5,  # High adoption: 50% higher scenario
    ],  # New validators per-epoch
})
```

```python
df_1, _exceptions = run(simulation_1)
```

```python
visualizations.plot_number_of_validators_over_time_foreach_subset(df_1)
```

The charts below visualize revenue and profit yields over time and across the three adoption scenarios shown above (i.e. implied ETH staked over time). The higher the adoption, the lower both revenue and profit yields.

```python
visualizations.plot_revenue_profit_yields_over_time_foreach_subset_subplots(
    df_1,
    subplot_titles=['Normal Validator Adoption', 'Low Validator Adoption', 'High Validator Adoption']
)
```

```python
visualizations.plot_revenue_profit_yields_over_time_foreach_subset(df_1)
```

```python
visualizations.plot_expanding_mean_revenue_profit_yields_over_time_foreach_subset(df_1)
```

# Analysis 2: Revenue and Profit Yields Over ETH Staked

This analysis allows the exploration of revenue and profit yields over a large range of ETH staked values. Compared to Analysis 1 (which assumed ETH staked ranges as a result of the adoption scenarios), Analysis 2 explicitly shows the yields validators can expect at certain points in the validator adoption curve. Profit yields are sensitive to ETH price in USD/ETH and plotted at two discrete points - 100 USD/ETH and the maximum ETH price over the last 12 months.

```python
df_2, _exceptions = run(simulation_2)
```

```python
visualizations.plot_revenue_profit_yields_over_eth_staked(df_2)
```

# Analysis 3: Revenue and Profit Yields Over ETH Price

This analysis allows the exploration of revenue and profit yields over a large range of ETH price values in USD/ETH. The ETH staked is fixed at the currrent ETH staked value updated from Etherscan. Revenue yields are not sensitive to ETH price, hence the horizontal line. Profit yields drop quickly at very low ETH prices and stabilize at higher ETH prices. Validator operational costs are fixed in USD, whereas revenue is in ETH, this causes a "cliff" in the realized profit (revenue - costs) at low ETH prices.

```python
simulation_3.model.params.update({
    'eth_staked_process': [
        # Current ETH staked value updated from Etherscan
        lambda _run, _timestep: eth_staked,
    ]
})
```

```python
df_3, _exceptions = run(simulation_3)
```

```python
visualizations.plot_revenue_profit_yields_over_eth_price(df_3)
```

# Analysis 4: Profit Yields Over ETH Staked vs. ETH Price

This contour chart was created to enable at-a-glance intuition about the relationship between profit yields, validator adoption, and ETH price (and because we like colorful charts). Profit yields are highest when the ETH price is high and adoption is low.

```python
df_4, _exceptions = run(simulation_4)
```

```python
fig = visualizations.plot_validator_environment_yield_contour(df_4)
fig.write_image("../outputs/validator_environment_yield_contour.png")
fig.show()
```

This surface chart displays the same data as the charts above and is arguably less readable, but since some folks might appreciate the fanciness of a 3D plot, we decided to keep it.

```python
visualizations.plot_validator_environment_yield_surface(df_4)
```

# Analysis 5: Profit Yields By Validator Environment Over Time

This analysis allows the exploration of revenue and profit yields per validator environment over time. The analysis is based on the "Normal Adoption" scenario described in Analysis 1. This analysis naturally heavily depends on the cost assumptions per validator environment, and we encourage the user to review the [assumptions document](../../ASSUMPTIONS.md) in this context.

StaaS validator environments, which don't incur validator operational costs directly, but instead pay a percentage of their total revenue as a fee to the relevant service provider, don't have variation in their profit yield with a stochastic (random) ETH price. Pool validator environments tend to receive better returns than StaaS environments, because their operational costs are shared among all the validators in the pool.

```python
simulation_5.model.params.update({'stage': [Stage.BEACON_CHAIN]})
```

```python
df_5, _exceptions = run(simulation_5)
```

```python
visualizations.plot_profit_yields_by_environment_over_time(df_5)
```
