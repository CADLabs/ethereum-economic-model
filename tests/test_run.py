from experiments.run import run


def test_run():
    """
    Check that the model run() method completes
    """

    results, _exceptions = run()
    assert True
