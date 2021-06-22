import itertools


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
    model = sim.model
    timesteps = sim.timesteps
    runs = sim.runs

    filtered_initial_state = filter(lambda x: isinstance(x, collections.Hashable), model.initial_state.items())
    initial_state_hashable = frozenset({key: value for key, value in filtered_initial_state})

    param_keys_hashable = tuple(model.params.keys())
    param_values = [value for param_list in model.params.values() for value in param_list]
    param_values_hashable = tuple(filter(lambda x: isinstance(x, collections.Hashable), param_values))

    to_hash = (initial_state_hashable, param_keys_hashable, param_values_hashable, timesteps, runs)

    return hash(to_hash)
