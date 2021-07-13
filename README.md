# CADLabs Ethereum Research Model
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

[![Python package](https://github.com/cadCAD-edu/ethereum-model/actions/workflows/python.yml/badge.svg)](https://github.com/cadCAD-edu/ethereum-model/actions/workflows/python.yml)

A modular dynamical systems model of Ethereum's validator economics, implemented using the open-source Python library [radCAD](https://github.com/cadCAD-edu/radCAD), a next-gen implementation of [cadCAD](https://cadcad.org). Implements the official Ethereum [Altair](https://github.com/ethereum/eth2.0-specs#altair) spec updates in the [Blue Loop / v1.1.0-alpha.7](https://github.com/ethereum/eth2.0-specs/releases/tag/v1.1.0-alpha.7) release.

## Table of Contents

* [Introduction](#introduction)
  * [Model Context](#model-context)
  * [Model Features](#model-features)
  * [Directory Structure](#directory-structure)
  * [Model Architecture](#model-architecture)
  * [Model Assumptions](#model-assumptions)
* [Environment Setup](#environment-setup)
* [Simulation Experiments](#simulation-experiments)
* [Model Extension Roadmap](#model-extension-roadmap)
* [Tests](#tests)
* [Change Log](#change-log)
* [Acknowledgements](#contributors)
* [License](#license)

---

## Introduction

### Model Context

This open-source model has been developed in collaboration with the Ethereum Robust Incentives Group, and funded by an Ethereum ESP (Ecosystem Support Program) grant. While originally scoped with purely modeling-educational intent as part of the cadCAD Edu online course "[cadCAD Masterclass: Ethereum Validator Economics](https://www.cadcad.education/course/masterclass-ethereum)", it has evolved to become a highly versatile, customizable and extensible research model, and includes a list of [model extension ideas](#roadmap). The model is focused on epoch- and population-level Ethereum validator economics across different deployment types and - at least in its initial setup - abstracts from slot- and agent-level dynamics. Please see [model assumptions](ASSUMPTIONS.md) for further context.

### Model Features

* Configurable to reflect protocol behavior at different points in time of the development roadmap (referred to as "upgrade stages"):
  * post Beacon Chain launch, pre EIP1559, pre PoS (validators receive PoS incentives, EIP1559 disabled, and PoW still in operation)
  * post Beacon Chain launch, post EIP1559, pre PoS (validators receive PoS incentives, EIP1559 enabled with miners receiving tips, and PoW still in operation)
  * post Beacon Chain launch, post EIP1559, post PoS (validators receive PoS incentives, EIP1559 enabled with validators receiving tips, and PoW deprecated)
* Flexible calculation granularity: By default, State Variables, System Metrics, and System Parameters are calculated at epoch level and aggregated daily (~= 225 epochs). Users can easily change epoch aggregation using the delta-time (dt) parameter. The model can be extended for slot-level granularity and analysis if that is desired (see [Model Extension Roadmap](#model-extension-roadmap).
* Supports [state-space analysis](https://en.wikipedia.org/wiki/State-space_representation) (i.e. simulation of system behavior over time) and [phase-space analysis](https://en.wikipedia.org/wiki/Phase_space) (i.e. generation of all unique system states in a given experimental setup).
* Customizable processes to set important variables such as ETH price, ETH staked, EIP1559 transaction pricing, and transaction rates.
* Modular model structure for convenient extension and modification. This allows different user groups to refactor the model for different purposes, rapidly test new incentive mechanisms, or to update the model as Ethereum implements new protocol improvements.
* References to official [Eth2 specs](https://github.com/ethereum/eth2.0-specs) in Policy and State Update Function logic. This enables seamless onboarding of protocol developers or for the more advanced cadCAD user to dig into the underlying protocol design that inspired the logic.

### Directory Structure

* [data/](data/): datasets used in model
* [docs/](docs/): various documentation including documentation of model software architecture using Python docstrings
* [experiments/](experiments/): analysis notebooks, experiment workflow configuration and execution
* [logs/](logs/): experiment log files
* [model/](model/): model software architecture (structural and configuration modules)
* [tests/](tests/): unit and integration tests for model and notebooks

### Model Architecture

The [model/](model/) directory contains the model's software architecture in the form of two categories of modules: structural modules and configuration modules.

#### Structural Modules

The model is composed of several structural modules in the [model/parts/](model/parts/) directory:

| Module | Description |
| --- | --- |
| [ethereum_system.py](model/parts/ethereum_system.py) | General Ethereum mechanisms, such as managing the system upgrade process, the EIP1559 transaction pricing mechanism, and updating the ETH price and ETH supply |
| [pos_incentives.py](model/parts/pos_incentives.py) | Proof of Stake incentives |
| [system_metrics.py](model/parts/system_metrics.py) | Calculation of validator costs, revenue, profit, and yield metrics |
| [validators.py](model/parts/validators.py) | Validator processes such as validator activation, staking, uptime |
| [utils/ethereum_spec.py](model/parts/utils/ethereum_spec.py) | Relevant extracts from the official Eth2 spec |

#### Configuration Modules

The model is configured using several configuration modules in the [model/](model/) directory:

| Module | Description |
| --- | --- |
| [constants.py](model/constants.py) | Constants used in the model e.g. number of epochs in a year, Gwei in 1 Ether |
| [simulation_configuration.py](model/simulation_configuration.py) | Simulation configuration such as the number of timesteps and Monte Carlo runs |
| [state_update_blocks.py](model/state_update_blocks.py) | cadCAD model state update block structure, composed of Policy and State Update Functions |
| [state_variables.py](model/state_variables.py) | Model State Variable definition, configuration, and defaults |
| [stochastic_processes.py](model/stochastic_processes.py) | Helper functions to generate stochastic environmental processes |
| [system_parameters.py](model/system_parameters.py) | Model System Parameter definition, configuration, and defaults |
| [types.py](model/types.py) | Various Python types used in the model, such as the `Stage` Enum and calculation units |
| [utils.py](model/utils.py) | Misc. utility and helper functions |

### Model Assumptions

The model implements the official Ethereum Specification wherever possible, but rests on a few default validator-level assumptions detailed in the [ASSUMPTIONS.md](ASSUMPTIONS.md) document.

## Environment Setup

1. Clone or download the Git repository: `git clone https://github.com/cadCAD-edu/ethereum-model` or using GitHub Desktop
2. If completing the cadCAD Edu Masterclass MOOC, check out the version `v1.0.0` tag: `git checkout tags/v1.0.0`
3. Set up your development environment using the [Setup](#setup) section
4. Follow the [Experiment Workflow](#experiment-workflow) section to execute your first experiment notebook!

### Setup

To set up your Python development environment, we cover two options:
* [Python Development Environment](#python-development-environment): Set up a custom development environment using Python 3 and Jupyter
* [Docker Development Environment](#docker-development-environment): Use the prebuilt Docker image

#### Python Development Environment

The following are prerequisites you'll need before completing the setup steps:
* Python: tested with versions 3.7, 3.8, 3.9
* NodeJS might be needed if using Plotly with Jupyter Lab (works out the box when using Anaconda/Conda package manager)

First, set up a Python 3 [virtualenv](https://docs.python.org/3/library/venv.html) development environment:
```bash
# Create a virtual environment using Python 3 venv module
python3 -m venv venv
# Activate virtual environment
source venv/bin/activate
```

Make sure to activate the virtual environment before each of the following steps.

Secondly, install the Python 3 dependencies using [Pip](https://packaging.python.org/tutorials/installing-packages/), from the [requirements.txt](requirements.txt) file, within your new virtual environment:
```bash
# Install Python 3 dependencies inside virtual environment
pip install -r requirements.txt
```

To create a new Jupyter Kernel specifically for this environment, execute the following command:
```bash
python3 -m ipykernel install --user --name python-cadlabs-eth-model --display-name "Python (CADLabs Ethereum Model)"
```

You'll then be able to select the kernel with display name `Python (CADLabs Ethereum Model)` to use for your notebook from within Jupyter.

To start Jupyter Notebook or Lab (see notes about issues with [using Plotly with Jupyter Lab](#known-issues)):
```bash
jupyter notebook
# Or:
jupyter lab
```

For more advanced Unix/macOS users, a [Makefile](Makefile) is also included for convenience and simply executes all the setup steps. For example to setup your environment and start Jupyter Lab:
```bash
# Setup environment
make setup
# Start Jupyter Lab
make start-lab
```

#### Docker Development Environment

If you'd rather use Docker, there is a prebuilt Docker image you can use to set up a Jupyter Lab development environment with all the dependencies you need.

See [CADLabs Jupyter Lab Environment](https://github.com/cadCAD-edu/jupyter-lab-environment)

#### Known Issues

###### Plotly doesn't display in Jupyter Lab

To install and use Plotly with Jupyter Lab, you might need NodeJS installed to build Node dependencies, unless you're using Anaconda/Conda package manager to manage your environment. Alternatively, use Jupyter Notebook which works out the box with Plotly.

See https://plotly.com/python/getting-started/

You might need to install the following "lab extension": 
```bash
jupyter labextension install jupyterlab-plotly@4.14.3
```

###### Windows issues

If you receive the following error and you use Anaconda, try: `conda install -c anaconda pywin32`
> DLL load failed while importing win32api: The specified procedure could not be found.

### Experiment Workflow

The default experiment, [experiments/default_experiment.py](experiments/default_experiment.py),
is an experiment that uses the default cadCAD System Parameters, Initial State, and State Update Blocks defined in the [models/](models/) directory.

To run the default experiment from the terminal, execute the `experiments.run` module:
```bash
python3 -m experiments.run
```

Alternatively, open and run one of the pre-existing Jupyter experiment notebooks in Jupyter Lab or Notebook,
following the [experiments/notebooks/README.ipynb](experiments/notebooks/0_README.ipynb) notebook as a guide.

## Simulation Experiments

The [experiments/](experiments/) directory contains modules for configuring and executing simulation experiments, as well as performing post-processing of the results.

The [experiments/notebooks/](experiments/notebooks/) directory contains several initial experiment notebooks we have created as a basis for analyzing the economics Ethereum validators are confronted with under a variety of scenarios.
These notebooks and analyses don't aim to comprehensively illuminate the Ethereum protocol, but rather to answer the most salient questions and serve as inspiration for building out more customized analyses and model extensions.

The [experiments/templates/](experiments/templates/) directory contains different experiment templates which can be used to create custom experiment notebooks.
See the [experiments/notebooks/README.ipynb](experiments/notebooks/0_README.ipynb) notebook for a walk-through of how to execute existing experiment notebooks, or configure and execute a new experiment.

#### Notebook 1. Model Validation

The purpose of this notebook is to recreate selected simulations from the widely acknowledged Hoban/Borgers Ethereum 2.0 Economic Model using the CADLabs model, and to compare the results. We suggest that the CADLabs model has a high degree of validity.

#### Notebook 2. Validator Revenue and Profit Yields (Validator-level Analysis)

The purpose of this notebook is to explore the returns validators can expect from staking in the Ethereum protocol across different time horizons, adoption scenarios, ETH price scenarios and validator environments.

* Analysis 1: Revenue and Profit Yields Over Time
* Analysis 2: Revenue and Profit Yields Over ETH Staked
* Analysis 3: Revenue and Profit Yields Over ETH Price
* Analysis 4: Profit Yields Over ETH Staked vs. ETH Price (Yield Surface)
* Analysis 5: Profit Yields By Validator Environment Over Time

#### Notebook 3. Network Issuance and Inflation Rate (Network-level Analysis)

The purpose of this notebook is to explore the ETH issuance and resulting annualized inflation rate across different time horizons and scenarios. 

* Analysis: Inflation Rate and ETH Supply Over Time

## Model Extension Roadmap

The modular nature of this model makes many exciting extensions and further analysis rather straightforward. The [Model Extension Roadmap](ROADMAP.md) provides some inspiration.

## Tests

We use Pytest to test the `model` module code, as well as the notebooks.

To execute the Pytest tests:
```bash
source venv/bin/activate
python3 -m pytest tests
```

To run the full GitHub Actions CI Workflow (see [.github/workflows](.github/workflows)):
```bash
source venv/bin/activate
make test
```

## Change Log

See [CHANGELOG.md](CHANGELOG.md) for notable changes and versions.

## Acknowledgements

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for contributions to this project repo.

Special thanks goes to:
* Ethereum 2.0 Economic Review. July 16, 2020. "An Analysis of Ethereum’s Proof of Stake Incentive Model". By Tanner Hoban and Thomas Borgers. For the extensive research that inspired the development of our model and the assumptions we adopted.

Other notable Ethereum PoS Models:
* Barnabé Monnot's **BeaconRunner** model: https://github.com/barnabemonnot/beaconrunner
* Pintail's **Beacon Chain Validator Rewards** model: https://pintail.xyz/posts/beacon-chain-validator-rewards/
* Flashbots **Eth2 Research** model - "Assessing the nature and impact of MEV in eth2.": https://github.com/flashbots/eth2-research

## License

`cadCAD-edu/ethereum-model` is licensed under the GNU General Public License v3.0.
 
Permissions of this strong copyleft license are conditioned on making available complete source code of licensed works and modifications, which include larger works using a licensed work, under the same license. Copyright and license notices must be preserved. Contributors provide an express grant of patent rights.

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://marthendalnunes.github.io/"><img src="https://avatars.githubusercontent.com/u/18421017?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Vitor Marthendal Nunes</b></sub></a><br /><a href="https://github.com/cadCAD-edu/ethereum-model/commits?author=marthendalnunes" title="Code">💻</a> <a href="#infra-marthendalnunes" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/cadCAD-edu/ethereum-model/pulls?q=is%3Apr+reviewed-by%3Amarthendalnunes" title="Reviewed Pull Requests">👀</a> <a href="https://github.com/cadCAD-edu/ethereum-model/commits?author=marthendalnunes" title="Documentation">📖</a> <a href="https://github.com/cadCAD-edu/ethereum-model/issues?q=author%3Amarthendalnunes" title="Bug reports">🐛</a> <a href="#ideas-marthendalnunes" title="Ideas, Planning, & Feedback">🤔</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!