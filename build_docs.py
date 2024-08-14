from jupyter_book.cli.main import main

# See https://stackoverflow.com/questions/74367920/sphinx-recursive-autosummary-not-importing-modules
# jupyter-book build --config docs/_config.yml --toc docs/_toc.yml --path-output docs .
main(["build", "--config", "docs/_config.yml", "--toc", "docs/_toc.yml", "--path-output", "docs", "."])
