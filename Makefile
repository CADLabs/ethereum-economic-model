build-docs:
	cp -r notebooks/* docs/notebooks/
	pdoc --html model -o docs --force
	jupyter-book build docs
