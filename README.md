# CADLabs Ethereum Validator Economics Model
[![Python package](https://github.com/cadCAD-edu/ethereum-model/actions/workflows/python.yml/badge.svg)](https://github.com/cadCAD-edu/ethereum-model/actions/workflows/python.yml)

A modular, highly extensible dynamical systems model implemented using the open-source radCAD Python library (TODO: ADD LINK TO CADLABS REPO)

**Official Eth2 specs version**: implements the [Altair](https://github.com/ethereum/eth2.0-specs#altair) updates in the [Beige Gorgon / v1.1.0-alpha.3](https://github.com/ethereum/eth2.0-specs/releases/tag/v1.1.0-alpha.3) release.

**Model Features**:
* Configurable to reflect protocol behavior at different points in time of the development roadmap:
  - post Beacon Chain launch, pre EIP1559, pre PoS (validators receive PoS incentives, EIP1559 disabled, and PoW still in operation)
  - post Beacon Chain launch, post EIP1559, pre PoS (validators receive PoS incentives, EIP1559 enabled with miners receiving tips, and PoW still in operation)
  - post Beacon Chain launch, post EIP1559, post PoS (validators receive PoS incentives, EIP1559 enabled with validators receiving tips, and PoW deprecated)
* Supports [state space analysis](https://en.wikipedia.org/wiki/State-space_representation) (i.e. simulation of system behavior over time) and [phase space analysis](https://en.wikipedia.org/wiki/Phase_space) (i.e. generation of all unique system states in a given experimental setup)
* Customizable processes to set important variables such as ETH price, ETH staked, EIP1559 transaction pricing, and transaction rates
* Modular model structure for convenient extension and modification. This allows different user groups to refactor the model for different purposes, rapidly test new incentive mechanisms, or to update the model as Ethereum implements new protocol improvements.
* References to official [Eth2 specs](https://github.com/ethereum/eth2.0-specs) in Policy and State Update Function logic. This enables seamless onboarding of protocol developers or for the more advanced cadCAD user to dig into the underlying protocol design that inspired the logic.

## Table of Contents
* [Context](#context)
* [Directory Structure](#directory-structure)
* [Model Architecture](#model-architecture)
* [Running Experiments](#running-experiments)
* [Development](#development)
* [Tests](#tests)
* [Jupyter Lab Environment](#jupyter-lab-environment)
* [Change Log](#change-log)
* [Contributors](#contributors)

---

## Context

(TODO: Describe in a few sentences how this model came about)

## Directory Structure
* [data/](data/): datasets used in model
* [docs/](docs/): work-in-progress documentation of model software architecture
* [experiments/](experiments/): experiment workflow configuration and execution
* [logs/](logs/): experiment log files
* [model/](model/): model structure, parts, and configuration
* [notebooks/](notebooks/): experiment analysis notebooks (TODO: Integrate into experiments directory, TBC)
* [outputs/](outputs/): experiment outputs (images, datasets, etc.)
* [tests/](tests/): unit and integration tests for model and notebooks

## Model Architecture

The model/ directory contains the model's software architecture in the form of two categories of modules: structural modules and configuration modules.

### Structural Modules (TODO: Discuss renaming modules and/or reordering code for better accessibiltiy)

The model is composed of different structural modules in the [model/parts/](model/parts/) directory:

| Module | Description |
| --- | --- |
| [ethereum.py](model/parts/ethereum.py) | Basic Ethereum mechanisms such as EIP1559 transaction pricing, and updates to ETH price and supply |
| [incentives.py](model/parts/incentives.py) | Calculation of Proof of Stake reward, penalty and slashing incentives |
| [metrics.py](model/parts/metrics.py) | Calculation of validator operational cost, revenue, profit, and yield metrics |
| [stages.py](model/parts/stages.py) | Management of stages of the Ethereum system upgrade process |
| [spec.py](model/parts/spec.py) | Relevant extracts from the official Eth2 spec |
| [validators.py](model/parts/validators.py) | Implementation of validator processes such as activation, staking, uptime |

### Configuration Modules

The model is configured using configuration modules in the [model/](model/) directory:

| Module | Description |
| --- | --- |
| [constants.py](model/constants.py) | Constants used in the model e.g. number of epochs in a year, Gwei in 1 Ether |
| [simulation_configuration.py](model/simulation_configuration.py) | Simulation configuration such as the number of timesteps and Monte Carlo runs |
| [state_update_blocks.py](model/state_update_blocks.py) | cadCAD model state update block structure, composed of Policy and State Update Functions |
| [state_variables.py](model/state_variables.py) | Model State Variable definition, configuration, and defaults |
| [stochastic_processes.py](model/stochastic_processes.py) | Helper functions to generate stochastic environmental processes |
| [system_parameters.py](model/system_parameters.py) | Model System Parameter definition, configuration, and defaults |
| [types.py](model/types.py) | Various types used in the model, such as the `Stage` Enum and calculation units |
| [utils.py](model/utils.py) | Misc. utility and helper functions |

## Running Experiments (TODO: Combine Notebooks into Experiment directory and make respective changes below)

The [experiments/](experiments/) directory contains modules for configuring and executing simulation experiments, as well as performing post-processing of the results.

The [experiments/templates/](experiments/templates/) directory contains different experiment templates which are used in the Jupyter experiment notebooks in the [notebooks/](notebooks/) directory to answer research questions and perform scenario analyses.

See the [notebooks/README.ipynb](notebooks/README.ipynb) notebook for a walk-through of how to configure and execute an experiment.

There are in total 8 experiment notebooks (TODO:Rename notebooks to match edited names below). These experiments answer specific research questions, and follow on logically from one to the next:

### 1. Model Validation

#### Research Question
Does the CADLabs model actually implement its <specification> and does it match the ? 

#### Notebook Overview
This experiment notebook is used to efficiently validate that the CADLabs model actually implements the Model Specification. Since the model specification is based on two main sources, the official Eth2 spec, and the (excellent) Hoban/Borgers Eth2 Economic Model (TODO: Add Link to Online Version), 

validates that the CADLabs model meets the (TODO: specify which specification we are talking about) specification by comparing multiple scenario analyses with those same analysis as per the (excellent) Hoban/Borgers Eth2 Economic Model (TODO: Add Link to Online Version).

### 2. Network Issuance

#### Research Question
What validator rewards and penalties make up network issuance?

#### Experiment Purpose
The purpose of this experiment is to explore the rewards and penalties that make up network issuance under different scenarios.

### 3. Network Costs

#### Research Question
What costs do validators incur to secure the network?

#### Experiment Purpose
The purpose of this experiment is to explore the cost incurred by validators to secure the network under different scenarios.

### 4. Network Yields

#### Research Question
What are the best and worst case network yields?

#### Experiment Purpose
The purpose of this experiment is to determine what the expected network yields are under different scenarios.

### 5. EIP1559 Transaction Pricing

#### Research Question
What effect will EIP1559 transaction pricing have on network yields?

#### Experiment Purpose
The purpose of this experiment is to explore the effect of the EIP1559 transaction pricing mechanism on network yields under different scenarios.

### 6. Utra-Sound Barrier

#### Research Question
At what point will the Ethereum system break the ultra-sound barrier (become deflationary), and what will the peak ETH supply be?

#### Experiment Purpose
The purpose of this experiment is to analyse the network suppy inflation, and determine under what scenarios the network becomes deflationary.

### 7. Validator Environment Yields

#### Research Question
What are the expected validator yields for staking in different environments?

#### Experiment Purpose
The purpose of this experiment is to explore the different validator environments and their yields under different scenarios.

### 8. Individual Validator Performance

#### Research Question
What is the performance of an individual validator with a custom environment configuration?

#### Experiment Purpose
The purpose of this experiment is to determine the performance of an individual validator using a custom environment configuration.

### Experiment Execution

The base experiment is an experiment that uses the default cadCAD System Parameters, Initial State, and State Update Blocks defined in the [models/](models/) directory. To run the base experiment from the terminal, execute the `experiments.run` module:
```bash
python3 -m experiments.run
```

Alternatively, open and run one of the Jupyter experiment notebooks in Jupyter Lab or Notebook.

### Experiment Workflow

1. Choose or create a new experiment template in the [experiments/templates/](experiments/templates/) directory
2. Copy the template experiment from [experiments/template.py](experiments/template.py) into the directory
3. Customize the base experiment using the template
4. Create a new Jupyter experiment notebook using the [notebooks/template.ipynb](notebooks/template.ipynb) experiment notebook template
5. Execute your experiment, post-process and analyze the results, and create Plotly charts!

## Development

A [Makefile](Makefile) is included for convenience, for example to setup your environment and start Jupyter Lab:

```bash
python3 -m venv venv
source venv/bin/activate

make setup # Setup environment
make start # Start Jupyter Lab
```

Otherwise, follow the steps below.

### Requirements

* Python versions: tested with 3.7, 3.8, 3.9
* Python dependencies: tested against versions in `requirements.txt`

### Setup

To setup a Python 3 development environment:
```bash
# Create a virtual environment using Python 3 venv module
python3 -m venv venv
# Activate virtual environment
source venv/bin/activate
# Install Python 3 dependencies inside virtual environment
pip install -r requirements.txt
```

## Tests

### Pytest Tests

To execute the Pytest tests:
```bash
source venv/bin/activate
python3 -m pytest tests
```

### Notebook Tests

```bash
source venv/bin/activate
make execute-notebooks
```

## Jupyter Environment

### Jupyter kernel

To setup your Jupyter Kernel within your virtual environment:
```bash
source venv/bin/activate
python3 -m ipykernel install --user --name python-cadlabs-eth-model --display-name "Python (CADLabs Ethereum Model)"
```

### Start environment

```bash
source venv/bin/activate
jupyter notebook
# Or Jupyter Lab, following additional steps below
jupyter lab
```

### Plotly Jupyter Lab support

To install and use Plotly with Jupyter Lab, you'll need NodeJS installed to build Node dependencies. Alternatively, use Jupyter Notebook which works out the box with Plotly.

See https://plotly.com/python/getting-started/

```bash
pip install jupyterlab "ipywidgets>=7.5"
jupyter labextension install jupyterlab-plotly@4.14.3
```

## Roadmap

The following is a non-exhaustive list of possible model extensions and future features:
* Implement the ability to simulate an inactivity leak scenario
* Implement a dynamic EIP1559 basefee with a feedback loop based on blockspace demand / network congestion
* Backtest the model against historical data such as the ETH price, ETH staked to determine expected historical yields
* Extend the model to cover future Ethereum upgrade stages after merge, such as sharding
* Apply Hoban/Borgers security (cost of attack) and required rate of return (RSAVY) analysis to simulation results
* ...

## Change Log

See [CHANGELOG.md](CHANGELOG.md) for notable changes and versions.

## Contributors

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for contributions to this project repo.

## Acknowledgements

* Ethereum 2.0 Economic Review. July 16, 2020. "An Analysis of Ethereum’s Proof of Stake Incentive Model". By Tanner Hoban and Thomas Borgers. For the extensive research that inspired the development of our model and the assumptions we adopted.
