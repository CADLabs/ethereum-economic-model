import inspect

import model
from model.state_update_blocks import state_update_blocks
from model.state_variables import initial_state
from model.system_parameters import parameters


def test_lint_state_variables():
    """Assert that the model State Variables are all used
    Assert that the State Variables contained in the State Update Blocks
    match the State Variables in the model's initial state.
    """

    # Get the set of all State Variable keys in State Update Blocks 'variables'
    state_update_blocks_state_variables = set(
        [
            state_variable
            for block in state_update_blocks
            for state_variable in block["variables"]
        ]
    )
    # Get the set of all State Variable keys in initial state
    initial_state_keys = set(initial_state.keys())

    # Assert the two sets share the same keys
    assert state_update_blocks_state_variables == initial_state_keys, (
        state_update_blocks_state_variables - initial_state_keys,
        initial_state_keys - state_update_blocks_state_variables,
    )


def test_lint_parameters():
    """Assert that the System Parameters are all used
    Assert that all System Parameters are used at least once in the
    model Policy or State Update Functions.
    """

    # Get all model modules
    model_modules = inspect.getmembers(model.parts, inspect.ismodule) + inspect.getmembers(model.parts.utils, inspect.ismodule)

    consts = [
        function.__code__.co_consts
        for (_key, module) in model_modules
        # Get all functions in module
        for (_key, function) in inspect.getmembers(module, inspect.isfunction)
        # Only include functions with __code__ attribute (i.e. no partial functions)
        if hasattr(function, "__code__")
    ]
    # Convert from list of tuples to a flat list
    consts = [item for tuple in consts for item in tuple]

    # Print all System Parameter keys not in consts
    print([key for key in parameters.keys() if key not in consts])
    # Assert all System Parameter keys are in consts
    assert all([key in consts for key in parameters.keys()])
