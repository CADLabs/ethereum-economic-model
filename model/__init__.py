"""
CADLabs Ethereum Economic Model
"""
__version__ = "1.1.7"

from radcad import Model

from model.system_parameters import parameters
from model.state_variables import initial_state
from model.state_update_blocks import state_update_blocks


# Instantiate a new Model
model = Model(
    params=parameters,
    initial_state=initial_state,
    state_update_blocks=state_update_blocks,
)
