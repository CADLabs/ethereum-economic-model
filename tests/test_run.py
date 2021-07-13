from experiments.run import run


def test_run():
    """
    Check that the model run() method completes
    """

    _results, _exceptions = run()
    assert True
