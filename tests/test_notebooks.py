import os


def test_notebooks():
    directory = "notebooks/"
    for notebook in os.listdir(directory):
        # NOTE We can't use glob library here, which only works on Unix systems
        if notebook.endswith(".ipynb"):
            result = os.popen(
                f"jupyter nbconvert --to script --execute --stdout {directory + notebook} | ipython"
            ).read()
            assert "1" in result
