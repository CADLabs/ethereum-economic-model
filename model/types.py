import numpy as np
import sys
from dataclasses import dataclass


# If Python version is greater than equal to 3.8, import from typing module
# Else also import from typing_extensions module
if sys.version_info >= (3, 8):
    from typing import TypedDict, List, Callable, NamedTuple
else:
    from typing import List, NamedTuple
    from typing_extensions import TypedDict, Callable


# Generic types
Uninitialized = np.nan
Percentage = float
Percentage_per_epoch = float

# Ethereum system types
Gas = int
Wei = int
Gwei = float
ETH = float

# US Dollar types
USD = float
USD_per_ETH = float
USD_per_epoch = float

# Simulation types
Run = int
Timestep = int

# Validator type for configuring distribution of validators as parameters
@dataclass
class ValidatorType:
    # Set the type (e.g. Percentage) and default value (e.g. 0.0) for each field
    type: str = ""
    percentage_distribution: Percentage = 0.0
    hardware_costs_per_epoch: USD_per_epoch = 0.0
    cloud_costs_per_epoch: USD_per_epoch = 0.0
    third_party_costs_per_epoch: Percentage_per_epoch = 0.0
