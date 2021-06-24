setup: install kernel plotly

install:
	pip install -r requirements.txt

kernel:
	python3 -m ipykernel install --user --name python-cadlabs-eth-model --display-name "Python (CADLabs Ethereum Model)"

plotly:
	jupyter labextension install jupyterlab-plotly@4.14.3

start-lab:
	jupyter lab

test:
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
	jupyter nbconvert --ExecutePreprocessor.timeout=-1 --execute --to notebook experiments/notebooks/*.ipynb

update-notebooks:
	jupyter nbconvert --ExecutePreprocessor.timeout=-1 --execute --to notebook --inplace experiments/notebooks/*.ipynb

clear-notebook-outputs:
	jupyter nbconvert --clear-output --inplace experiments/notebooks/*.ipynb
