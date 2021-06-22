import itertools
import types as types
import collections


def generate_cartesion_product(sweeps):
    """Generates a parameter sweep using a cartesion product of System Parameter dictionary

        Args:
            sweeps (Dict[str, List]): A cadCAD System Parameter dictionary to sweep

        Returns:
            Dict: A dictionary containing the cartesian product of all parameters
    """
    cartesian_product = list(itertools.product(*sweeps.values()))
    params = {key: [x[i] for x in cartesian_product] for i, key in enumerate(sweeps.keys())}
    return params


def get_simulation_hash(sim):
    # Get inputs for hash function
    model = sim.model
    timesteps = sim.timesteps
    runs = sim.runs

    # Filter out unhashable types
    initial_state = filter(lambda x: isinstance(x, collections.Hashable), model.initial_state.items())
    # Create a hashable frozen set from dictionary
    initial_state = frozenset({key: value for key, value in initial_state})

    param_keys = tuple(model.params.keys())
    param_values = [value for param_list in model.params.values() for value in param_list]
    # Convert unhashable types to code
    param_values = [value.__code__ if isinstance(value, types.FunctionType) else None for value in param_values]
    # Filter out unhashable types
    param_values = tuple(filter(lambda x: isinstance(x, collections.Hashable), param_values))

    # Create tuple of all hash inputs
    to_hash = (initial_state, param_keys, param_values, timesteps, runs)

    return hash(to_hash)
