"""
Helper functions to generate stochastic environmental processes
"""

import numpy as np
from stochastic import processes

import experiments.simulation_configuration as simulation
from experiments.utils import rng_generator


def create_polygn_price_process(
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    rng=np.random.default_rng(1),
    minimum_polygn_price=0.9,
):
    """Configure environmental ETH price process

    > A Brownian excursion is a Brownian bridge from (0, 0) to (t, 0) which is conditioned to be non-negative on the interval [0, t].

    See https://stochastic.readthedocs.io/en/latest/continuous.html
    """
    process = processes.continuous.BrownianExcursion(t=(timesteps * dt), rng=rng)
    samples = process.sample(timesteps * dt + 1)
    maximum_eth_price = max(samples)
    samples = [
        minimum_polygn_price + eth_price_sample / maximum_eth_price * minimum_polygn_price
        for eth_price_sample in samples
    ]
    samples = [minimum_polygn_price + (5-minimum_polygn_price)*i/len(samples)  for i in range(len(samples))]
    return samples


def create_validator_process(
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    rng=np.random.default_rng(1),
    validator_adoption_rate=4,
):
    """Configure environmental validator staking process

    > A Poisson process with rate lambda is a count of occurrences of i.i.d. exponential random variables with mean 1/lambda. This class generates samples of times for which cumulative exponential random variables occur.

    See https://stochastic.readthedocs.io/en/latest/continuous.html
    """
    process = processes.continuous.PoissonProcess(
        rate=1 / validator_adoption_rate, rng=rng
    )
    samples = process.sample(timesteps * dt + 1)
    samples = np.diff(samples)
    samples = [int(sample) for sample in samples]
    return samples


def create_stochastic_process_realizations(
    process,
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    runs=5,
):
    """Create stochastic process realizations

    Using the stochastic processes defined in `processes` module, create random number generator (RNG) seeds,
    and use RNG to pre-generate samples for number of simulation timesteps.
    """

    switcher = {
        "polygn_price_samples": [
            create_polygn_price_process(timesteps=timesteps, dt=dt, rng=rng_generator())
            for _ in range(runs)
        ],
        "validator_samples": [
            create_validator_process(timesteps=timesteps, dt=dt, rng=rng_generator())
            for _ in range(runs)
        ],
        "validator_uptime_samples": [
            rng_generator().uniform(0.96, 0.99, timesteps * dt + 1) for _ in range(runs)
        ],
    }

    return switcher.get(process, "Invalid Process")
