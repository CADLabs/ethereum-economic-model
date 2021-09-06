import itertools
import types as types
import collections
import inspect
import numpy as np

from IPython.display import Code
from pygments.formatters import HtmlFormatter
from IPython.core.display import HTML


def rng_generator(master_seed=1):
    """Generate a sequence of Numpy RNG seeds

    This method can be initialized using a master seed with `rng_generator(123)`.
    If it isn't initialized, the first call to `rng_generator()`
    will both initialize the seed sequence and return an RNG with the first seed of the sequence.

    Every time the method is called without arguments, it generates a new seed with a reproducible sequence.

    This is useful, for example, if you wanted to have a number of stochastic processes
    with unique seeds across different runs, but reproducible results across simulations.
    """
    global seed_sequence
    if 'seed_sequence' not in globals():
        rng = np.random.default_rng(master_seed)
        seed_sequence = rng.bit_generator._seed_seq
        return np.random.default_rng(seed_sequence.spawn(1)[0])
    else:
        return np.random.default_rng(seed_sequence.spawn(1)[0])


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


def display_code(code):
    """Inspect Python modules, functions and return the syntax highlighted code
    """
    formatter = HtmlFormatter()
    display(HTML(f'<style>{formatter.get_style_defs(".highlight")}</style>'))

    return Code(inspect.getsource(code), language='python')
