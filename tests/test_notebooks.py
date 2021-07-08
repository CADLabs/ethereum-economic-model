import os


def test_notebooks():
    """Test all Jupyter Notebooks
    Test that the notebooks run to completion
    NOTE We can't use glob library here, which only works on Unix systems
    """
    directory = "experiments/notebooks/"
    for notebook in os.listdir(directory):
        if notebook.endswith(".ipynb"):
            result = os.popen(
                f"jupyter nbconvert --to script --execute --stdout {directory + notebook} | ipython"
            ).read()
            assert "1" in result
