from model.constants import epochs_per_month

DELTA_TIME = 100  # epochs per timestep
SIMULATION_TIME_MONTHS = 12  # number of months
TIMESTEPS = (
    epochs_per_month * SIMULATION_TIME_MONTHS // DELTA_TIME
)  # number of simulation timesteps
MONTE_CARLO_RUNS = 1  # number of runs
