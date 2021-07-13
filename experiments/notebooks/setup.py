import sys
import pandas as pd
from IPython import get_ipython


ipython = get_ipython()

# Find performance bottlenecks by timing Python cell execution
ipython.magic("load_ext autotime") # ipython.magic("...") is equivalent to % in Jupyter cell

# Reload all modules (except those excluded by %aimport) every time before executing the Python code typed
# See https://ipython.org/ipython-doc/stable/config/extensions/autoreload.html
ipython.magic("load_ext autoreload")
ipython.magic("autoreload 2")

# Append the root directory to Python path,
# this allows you to store notebooks in `experiments/notebooks/` sub-directory and access model Python modules
sys.path.append("../..")
sys.path.append("../../..")

# Configure Pandas to raise for chained assignment, rather than warn, so that we can fix the issue!
pd.options.mode.chained_assignment = 'raise'

# Set plotly as the default plotting backend for pandas
pd.options.plotting.backend = "plotly"
