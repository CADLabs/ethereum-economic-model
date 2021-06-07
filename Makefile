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
	# sed -i 's/\"index.html/\"model\/index.html/g' ./docs/model/*.html

docs-jupyter-book:
	rm -rf docs/notebooks/*
	cp -r notebooks/* docs/notebooks/
	sed -i 's/media/_static/g' ./docs/notebooks/*.ipynb
	jupyter-book clean docs
	jupyter-book build docs

serve-docs:
	gunicorn -w 4 -b 127.0.0.1:5000 docs.server:app

execute-notebooks:
	jupyter nbconvert --execute --to notebook notebooks/*.ipynb

update-notebooks:
	jupyter nbconvert --execute --to notebook --inplace notebooks/*.ipynb
