import os


def test_scratchpad_notebook():
    notebook = "notebooks/scratchpad.ipynb"
    result = os.popen(f"jupyter nbconvert --to script --execute --stdout {notebook} | ipython").read()
    assert "1" in result
