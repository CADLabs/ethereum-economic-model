from model.parameters import Parameters
from model.parameters import parameters


def test_parameters_type():
    typed_dict_keys = set(Parameters.__annotations__.keys())
    parameters_keys = set(parameters.keys())
    assert typed_dict_keys == parameters_keys, (
        parameters_keys - typed_dict_keys,
        typed_dict_keys - parameters_keys,
    )
