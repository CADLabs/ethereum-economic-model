<p align="center">
  <img src="https://github.com/cadCAD-edu/eth2-masterclass/blob/main/media/eth-masterclass-horizontal.png" width="50%" />
</p>

# Ethereum Validator Economics Model
[![Python package](https://github.com/cadCAD-edu/eth2.0-masterclass/actions/workflows/python.yml/badge.svg)](https://github.com/cadCAD-edu/eth2.0-masterclass/actions/workflows/python.yml)

An Ethereum Validator Economics model.

**Eth2 specs version**: implements the [Altair](https://github.com/ethereum/eth2.0-specs#altair) updates in the [Beige Gorgon / v1.1.0-alpha.3](https://github.com/ethereum/eth2.0-specs/releases/tag/v1.1.0-alpha.3) release.

Features:
* Simulate the different phases of the Ethereum system upgrade process (Phase 0, EIP1559 enabled, The Merge)
* Enables both state space (simulation over time) and phase space (analysis of system state) simulations and analyses
* Customizable processes for ETH price, ETH staked, validator adoption, EIP1559, and transaction rates
* Modular model structure
* References to [Eth2 specs](https://github.com/ethereum/eth2.0-specs) in Policy and State Update Function logic

## Table of Contents
* [Model](#model)
* [Experiments](#experiments)
* [Development](#development)
* [Tests](#tests)
* [Jupyter Lab Environment](#jupyter-lab-environment)
* [Change Log](#change-log)
* [Contributors](#contributors)

## Directory Structure
* [data/](data/): datasets used in model (e.g. for stochastic processes)
* [docs/](docs/): work-in-progress documentation of model software architecture
* [experiments/](experiments/): experiment workflow configuration and execution
* [logs/](logs/): experiment log files
* [model/](model/): model structure, parts, and configuration
* [notebooks/](notebooks/): experiment analysis notebooks
* [outputs/](outputs/): experiment outputs (images, datasets, etc.)
* [tests/](tests/): unit and integration tests for model and notebooks

---

## Model

### Parts

The model is composed of different modules in the [model/parts/](model/parts/) directory:

| Module | Description |
| --- | --- |
| [ethereum.py](model/parts/ethereum.py) | Genereal Ethereum mechanisms, such as the EIP1559 transaction pricing mechanism, and updating the ETH price and ETH supply |
| [incentives.py](model/parts/incentives.py) | Proof of Stake incentives |
| [metrics.py](model/parts/metrics.py) | Calculation of validator costs, revenue, profit, and yield metrics |
| [phases.py](model/parts/phases.py) | Management of phases of the Ethereum system upgrade process |
| [spec.py](model/parts/spec.py) | Relevant extracts from the Eth2 spec |
| [validators.py](model/parts/validators.py) | Validator processes such as validator activation, staking, uptime |

### Configuration

The model is configured using modules in the [model/](model/) directory:

| Module | Description |
| --- | --- |
| [constants.py](model/constants.py) | Constants used in the model e.g. number of epochs in a year, Gwei in 1 Ether |
| [parameters.py](model/parameters.py) | Model System Parameter definition, configuration, and defaults |
| [processes.py](model/processes.py) | Helper functions to generate stochastic environmental processes |
| [simulation_configuration.py](model/simulation_configuration.py) | Simulation configuration such as the number of timesteps and Monte Carlo runs |
| [state_update_blocks.py](model/state_update_blocks.py) | cadCAD model state update block structure, composed of Policy and State Update Functions |
| [state_variables.py](model/state_variables.py) | Model State Variable definition, configuration, and defaults |
| [types.py](model/types.py) | Various types used in the model, such as the `Phase` Enum and calculation units |
| [utils.py](model/utils.py) | Misc. utility and helper functions |

## Experiments

The [experiments/](experiments/) directory contains different experiment templates which are used in the Jupyter experiment notebooks in the [notebooks/](notebooks/) directory to answer research questions and perform scenario analyses.

See the [experiments/README.ipynb](experiments/README.ipynb) notebook for a walk-through of how to configure and execute an experiment.

There are in total 8 experiment notebooks. These experiments answer specific research questions, and follow on logically from one to the next:

### 1. Model Validation

#### Research Question
> How do we validate the model meets the specification?

#### Experiment Purpose
The purpose of this experiment is to validate whether the model meets the specification by comparing multiple scenario analyses seen in the Hoban/Borgers Economic Model with those same analyses performed with our model.

### 2. Network Issuance

#### Research Question
> What validator rewards and penalties make up network issuance?

#### Experiment Purpose
The purpose of this experiment is to explore the rewards and penalties that make up network issuance under different scenarios.

### 3. Network Costs

#### Research Question
> What costs do validators incur to secure the network?

#### Experiment Purpose
The purpose of this experiment is to explore the cost incurred by validators to secure the network under different scenarios.

### 4. Network Yields

#### Research Question
> What are the best and worst case network yields?

#### Experiment Purpose
The purpose of this experiment is to determine what the expected network yields are under different scenarios.

### 5. EIP1559 Transaction Pricing

> What effect will EIP1559 transaction pricing have on network yields?

#### Experiment Purpose
The purpose of this experiment is to explore the effect of the EIP1559 transaction pricing mechanism on network yields under different scenarios.

### 6. Utra-Sound Barrier

#### Research Question
> At what point will the Ethereum system break the ultra-sound barrier (become deflationary), and what will the peak ETH supply be?

#### Experiment Purpose
The purpose of this experiment is to analyse the network suppy inflation, and determine under what scenarios the network becomes deflationary.

### 7. Validator Environment Yields

#### Research Question
> What are the expected validator yields for staking in different environments?

#### Experiment Purpose
The purpose of this experiment is to explore the different validator environments and their yields under different scenarios.

### 8. Individual Validator Performance

#### Research Question
> What is the performance of an individual validator with a custom environment configuration?

#### Experiment Purpose
The purpose of this experiment is to determine the performance of an individual validator using a custom environment configuration.

### Experiment Execution

The base experiment template is an experiment that uses the default cadCAD System Parameters, Initial State, and State Update Blocks defined in the [models/](models/) directory. To run the base experiment from the terminal, execute the `experiments.run` module:
```bash
python3 -m experiments.run
```

Alternatively, open and run one of the Jupyter experiment notebooks in Jupyter Lab.

### Experiment Workflow

1. Choose or create a new experiment template in the [experiments/templates/](experiments/templates/) directory
2. Copy the template experiment from [experiments/template.py](experiments/template.py) into the directory
3. Customize the base experiment using the template
4. Create a new Jupyter experiment notebook using the [notebooks/_template.ipynb](notebooks/_template.ipynb) experiment notebook template
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

To run the tests using Pytest:
```bash
source venv/bin/activate
python3 -m pytest tests
```

## Jupyter Environment

### Jupyter kernel

To setup your Jupyter Kernel within your virtual environment:
```bash
source venv/bin/activate
python3 -m ipykernel install --user --name python-eth2 --display-name "Python (Eth2)"
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
* Implement a dynamic EIP1559 basefee with a feedback loop based on blockspace demand / network congestion
* Backtest the model against historical data such as the ETH price, ETH staked to determine expected historical yields
* Extend the model to cover future Eth2 phases after merge, such as sharding
* Apply Hoban/Borgers security (cost of attack) and required rate of return (RSAVY) analysis to simulation results
* ...

## Change Log

See [CHANGELOG.md](CHANGELOG.md) for notable changes and versions.

## Contributors

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for contributions to this project repo.

## Acknowledgements
