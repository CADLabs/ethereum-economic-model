from model.state_variables import StateVariables
from model.state_variables import initial_state


def test_initial_state_type():
    # NOTE TypedDict doesn't support `assert isinstance(initial_state, StateVariables)`
    typed_dict_keys = set(StateVariables.__annotations__.keys())
    state_variables_keys = set(initial_state.keys())
    assert typed_dict_keys == state_variables_keys, (
        state_variables_keys - typed_dict_keys,
        typed_dict_keys - state_variables_keys,
    )
