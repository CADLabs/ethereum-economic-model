"""
Helper functions to generate stochastic environmental processes
"""

import numpy as np
from stochastic import processes

import model.simulation_configuration as simulation


def create_eth_price_process(
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    rng=np.random.default_rng(1),
    minimum_eth_price=1500,
):
    """Configure environmental ETH price process
    > A Brownian excursion is a Brownian bridge from (0, 0) to (t, 0) which is conditioned to be nonnegative on the interval [0, t].

    See https://stochastic.readthedocs.io/en/latest/continuous.html
    """
    process = processes.continuous.BrownianExcursion(t=(timesteps * dt), rng=rng)
    samples = process.sample(timesteps * dt + 1)
    maximum_eth_price = max(samples)
    samples = [
        minimum_eth_price + eth_price_sample / maximum_eth_price * minimum_eth_price
        for eth_price_sample in samples
    ]
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
    process = processes.continuous.PoissonProcess(rate=1 / 3, rng=rng)
    samples = process.sample(timesteps * dt + 1)
    samples = np.diff(samples)
    samples = [int(sample) for sample in samples]
    return samples


def create_stochastic_process_realizations(
    timesteps=simulation.TIMESTEPS,
    dt=simulation.DELTA_TIME,
    runs=simulation.MONTE_CARLO_RUNS,
):
    """Create stochastic process realizations
    Using the stochastic processes defined in `processes` module, create random number generator (RNG) seeds,
    and use RNG to pre-generate samples for number of simulation timesteps.
    """
    
     # Create Random Number Generator (RNG) with a seed from which child seeds can be generated for range of runs and sub processes.
    
    master_seed=1234
    master_rng = np.random.default_rng(master_seed)
    master_seed_sequence = master_rng.bit_generator._seed_seq
    
         
    # Create Random Number Generator (RNG) with a seed for range of runs
    rngs = [np.random.default_rng(master_seed_sequence.spawn(1)[0]) for _ in range(runs)]

    eth_price_samples = [
        create_eth_price_process(timesteps=timesteps, dt=dt, rng=rng) for rng in rngs
    ]
    validator_samples = [
        create_validator_process(timesteps=timesteps, dt=dt, rng=rng) for rng in rngs
    ]
    validator_uptime_samples = [
        rng.uniform(0.96, 0.99, timesteps * dt + 1) for rng in rngs
    ]

    return {
        "eth_price_samples": eth_price_samples,
        "validator_samples": validator_samples,
        "validator_uptime_samples": validator_uptime_samples,
    }
