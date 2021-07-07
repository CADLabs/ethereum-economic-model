"""
Various Python types used in the model
"""

import numpy as np
import sys

# See https://docs.python.org/3/library/dataclasses.html
from dataclasses import dataclass, field
from enum import Enum

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
Gwei_per_Gas = float
ETH = float


class Stage(Enum):
    """Stages of the Ethereum network upgrade process finite-state machine"""

    ALL = 1
    """Transition through all stages"""
    BEACON_CHAIN = 2
    """Beacon Chain implemented; EIP1559 disabled; POW issuance enabled"""
    EIP1559 = 3
    """Beacon Chain implemented; EIP1559 enabled; POW issuance enabled"""
    PROOF_OF_STAKE = 4
    """Beacon Chain implemented; EIP1559 enabled; POW issuance disabled"""


# US Dollar types
USD = float
USD_per_ETH = float
USD_per_epoch = float

# Simulation types
Run = int
Timestep = int

# BeaconState types
Epoch = int

# Validator types
ValidatorIndex = int


# Validator environment class used for configuring distribution of validators as parameters
@dataclass
class ValidatorEnvironment:
    # Set the type (e.g. Percentage) and default value (e.g. 0.0) for each field
    type: str = ""
    percentage_distribution: Percentage = 0.0
    hardware_costs_per_epoch: USD_per_epoch = 0.0
    cloud_costs_per_epoch: USD_per_epoch = 0.0
    third_party_costs_per_epoch: Percentage_per_epoch = 0.0
