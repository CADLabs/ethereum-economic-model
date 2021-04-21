import pandas as pd
from functools import partial
import datetime
from radcad.core import generate_parameter_sweep

import model.simulation_configuration as simulation
import model.constants as constants
from model.parameters import parameters, Parameters, validator_types


def assign_parameters(df: pd.DataFrame, parameters: Parameters, set_params=[]):
    parameter_sweep = generate_parameter_sweep(parameters)
    parameter_sweep = [{param: subset[param] for param in set_params} for subset in parameter_sweep]

    for subset_index in df['subset'].unique():
        for (key, value) in parameter_sweep[subset_index].items():
            df.loc[df.eval(f'subset == {subset_index}'), key] = value

    return df


def post_process(df: pd.DataFrame):
    # Assign parameters to DataFrame
    assign_parameters(df, parameters, [
        # Parameters to assign to DataFrame
    ])

    # Set timestamps
    now = datetime.datetime.now()
    df['timestamp'] = df.apply(lambda row: now + datetime.timedelta(days=(
        row["timestep"] * (simulation.DELTA_TIME / constants.epochs_per_day)
    )), axis=1)

    # Dissagregate validator costs
    df[[validator.type + '_hardware_costs' for validator in validator_types]] = df.apply(lambda row: list(row.validator_hardware_costs), axis=1, result_type='expand').astype('float64')
    df[[validator.type + '_cloud_costs' for validator in validator_types]] = df.apply(lambda row: list(row.validator_cloud_costs), axis=1, result_type='expand').astype('float64')
    df[[validator.type + '_third_party_costs' for validator in validator_types]] = df.apply(lambda row: list(row.validator_third_party_costs), axis=1, result_type='expand').astype('float64')

    # Dissagregate yields
    df[[validator.type + '_revenue_yields' for validator in validator_types]] = df.apply(lambda row: list(row.validator_revenue_yields), axis=1, result_type='expand').astype('float64')
    df[[validator.type + '_profit_yields' for validator in validator_types]] = df.apply(lambda row: list(row.validator_profit_yields), axis=1, result_type='expand').astype('float64')

    # Convert decimals to percentages
    df['supply_inflation_pct'] = df['supply_inflation'] * 100
    df['total_revenue_yields_pct'] = df['total_revenue_yields'] * 100
    df['total_profit_yields_pct'] = df['total_profit_yields'] * 100

    # Convert validator rewards from Gwei to ETH
    validator_rewards = ['source_reward', 'target_reward', 'head_reward', 'block_proposer_reward', 'sync_reward']
    df[[reward + '_eth' for reward in validator_rewards]] = df[validator_rewards] / constants.gwei

    # Drop the initial state for plotting
    df = df.drop(df.query('timestep == 0').index)

    return df
