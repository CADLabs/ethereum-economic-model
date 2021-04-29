setup: install kernel plotly

install:
	pip install -r requirements.txt

kernel:
	python3 -m ipykernel install --user --name python-eth2 --display-name "Python (Eth2)"

plotly:
	jupyter labextension install jupyterlab-plotly@4.14.3

start-lab:
	jupyter lab

test:
	python3 -m pytest tests

build-docs: docs-pdoc docs-jupyter-book

docs-pdoc:
	pdoc --html model -o docs --force

docs-jupyter-book:
	cp -r notebooks/* docs/notebooks/
	jupyter-book build docs

execute-notebooks:
	jupyter nbconvert --execute --to notebook --inplace notebooks/*.ipynb
