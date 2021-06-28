import itertools


def generate_cartesian_product(sweeps):
    """Generates a parameter sweep using a cartesian product of System Parameter dictionary

        Args:
            sweeps (Dict[str, List]): A cadCAD System Parameter dictionary to sweep

        Returns:
            Dict: A dictionary containing the cartesian product of all parameters
    """
    cartesian_product = list(itertools.product(*sweeps.values()))
    params = {key: [x[i] for x in cartesian_product] for i, key in enumerate(sweeps.keys())}
    return params
