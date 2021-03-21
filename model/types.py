import numpy as np
import sys


if sys.version_info >= (3, 8):
    from typing import TypedDict, List, Callable
else:
    from typing import List
    from typing_extensions import TypedDict, Callable


Uninitialized = np.nan

Percentage = float

Gas = int
Wei = int
Gwei = float
ETH = float

USD = float
USD_per_ETH = float

Run = int
Timestep = int

validator_types = [
    'diy_hardware',
    'diy_cloud',
    'pool_staas',
    'pool_hardware',
    'pool_cloud',
    'staas_full',
    'staas_self_custodied',
]
