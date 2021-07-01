setup: install kernel plotly

install:
	pip install -r requirements.txt

kernel:
	python3 -m ipykernel install --user --name python-cadlabs-eth-model --display-name "Python (CADLabs Ethereum Model)"

plotly:
	jupyter labextension install jupyterlab-plotly@4.14.3

start-lab:
	jupyter lab

test: execute-notebooks
	# Check formatting
	python -m black --check --diff model
	# Check docstrings
	pylint --disable=all --enable=missing-docstring model
	# Run Pytest tests
	python3 -m pytest tests

build-docs: docs-pdoc docs-jupyter-book

docs-pdoc:
	pdoc --html model -o docs --force
	# sed -i 's/\"index.html/\"model\/index.html/g' ./docs/model/*.html

docs-jupyter-book:
	rm -rf docs/notebooks/*
	cp -r experiments/notebooks/* docs/notebooks/
	sed -i 's/media/_static/g' ./docs/notebooks/*.ipynb
	jupyter-book clean docs
	jupyter-book build --config docs/_config.yml --toc docs/_toc.yml --path-output docs .

serve-docs:
	gunicorn -w 4 -b 127.0.0.1:5000 docs.server:app

execute-notebooks:
	rm experiments/notebooks/*.nbconvert.* || true
	jupyter nbconvert --ExecutePreprocessor.timeout=-1 --ExecutePreprocessor.kernel_name=python-cadlabs-eth-model --execute --to notebook experiments/notebooks/*.ipynb
	rm experiments/notebooks/*.nbconvert.* || true

update-notebooks:
	rm experiments/notebooks/*.nbconvert.* || true
	jupyter nbconvert --ExecutePreprocessor.timeout=-1 --ExecutePreprocessor.kernel_name=python-cadlabs-eth-model --execute --to notebook --inplace experiments/notebooks/*.ipynb
	rm experiments/notebooks/*.nbconvert.* || true

clear-notebook-outputs:
	jupyter nbconvert --clear-output --inplace experiments/notebooks/*.ipynb
