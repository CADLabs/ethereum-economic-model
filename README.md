# cadCAD Edu Eth2 MasterClass
[![Python package](https://github.com/cadCAD-edu/eth2.0-masterclass/actions/workflows/python.yml/badge.svg)](https://github.com/cadCAD-edu/eth2.0-masterclass/actions/workflows/python.yml)

TODO: description

## Table of Contents
* [Experiments](#experiments)
* [Development](#development)
* [Tests](#tests)
* [Jupyter Lab Environment](#jupyter-lab-environment)

---

## Experiments

```bash
python3 -m experiments.run
```

## Development

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
python3 -m pytest tests
```

## Jupyter Lab Environment

## Jupyter kernel

```bash
python3 -m ipykernel install --user --name python3-edu-eth2-masterclass
```

## Plotly Jupyter Lab support

See https://plotly.com/python/getting-started/

```bash
pip install jupyterlab "ipywidgets>=7.5"
jupyter labextension install jupyterlab-plotly@4.14.3
```
