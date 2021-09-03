import pandas as pd
from radcad.core import generate_parameter_sweep

import model.constants as constants
from model.system_parameters import parameters, Parameters, validator_environments


def assign_parameters(df: pd.DataFrame, parameters: Parameters, set_params=[]):
    if set_params:
        parameter_sweep = generate_parameter_sweep(parameters)
        parameter_sweep = [{param: subset[param] for param in set_params} for subset in parameter_sweep]

        for subset_index in df['subset'].unique():
            for (key, value) in parameter_sweep[subset_index].items():
                df.loc[df.eval(f'subset == {subset_index}'), key] = value

    return df


def post_process(df: pd.DataFrame, drop_timestep_zero=True, parameters=parameters):
    # Assign parameters to DataFrame
    assign_parameters(df, parameters, [
        # Parameters to assign to DataFrame
        'dt'
    ])

    # Dissagregate validator count
    df[[validator.type + '_validator_count' for validator in validator_environments]] = df.apply(lambda row: list(row.validator_count_distribution), axis=1, result_type='expand').astype('float32')

    # Dissagregate validator costs
    df[[validator.type + '_costs' for validator in validator_environments]] = df.apply(lambda row: list(row.validator_costs), axis=1, result_type='expand').astype('float32')
    df[[validator.type + '_hardware_costs' for validator in validator_environments]] = df.apply(lambda row: list(row.validator_hardware_costs), axis=1, result_type='expand').astype('float32')
    df[[validator.type + '_cloud_costs' for validator in validator_environments]] = df.apply(lambda row: list(row.validator_cloud_costs), axis=1, result_type='expand').astype('float32')
    df[[validator.type + '_third_party_costs' for validator in validator_environments]] = df.apply(lambda row: list(row.validator_third_party_costs), axis=1, result_type='expand').astype('float32')

    # Dissagregate individual validator costs
    _mapping = dict(zip(
        [validator.type + '_costs' for validator in validator_environments],
        [validator.type + '_validator_count' for validator in validator_environments]
    ))

    df[['individual_validator_' + validator.type + '_costs' for validator in validator_environments]] = \
        df[[validator.type + '_costs' for validator in validator_environments]].rename(columns=_mapping) / \
        df[[validator.type + '_validator_count' for validator in validator_environments]]

    # Dissagregate revenue and profit
    df[[validator.type + '_revenue' for validator in validator_environments]] = df.apply(lambda row: list(row.validator_revenue), axis=1, result_type='expand').astype('float32')
    df[[validator.type + '_profit' for validator in validator_environments]] = df.apply(lambda row: list(row.validator_profit), axis=1, result_type='expand').astype('float32')

    # Dissagregate yields
    df[[validator.type + '_revenue_yields' for validator in validator_environments]] = df.apply(lambda row: list(row.validator_revenue_yields), axis=1, result_type='expand').astype('float32')
    df[[validator.type + '_profit_yields' for validator in validator_environments]] = df.apply(lambda row: list(row.validator_profit_yields), axis=1, result_type='expand').astype('float32')

    # Convert decimals to percentages
    df[[validator.type + '_revenue_yields_pct' for validator in validator_environments]] = df[[validator.type + '_revenue_yields' for validator in validator_environments]] * 100
    df[[validator.type + '_profit_yields_pct' for validator in validator_environments]] = df[[validator.type + '_profit_yields' for validator in validator_environments]] * 100
    df['supply_inflation_pct'] = df['supply_inflation'] * 100
    df['total_revenue_yields_pct'] = df['total_revenue_yields'] * 100
    df['total_profit_yields_pct'] = df['total_profit_yields'] * 100

    # Calculate revenue-profit yield spread
    df['revenue_profit_yield_spread_pct'] = df['total_revenue_yields_pct'] - df['total_profit_yields_pct']

    # Convert validator rewards from Gwei to ETH
    validator_rewards = [
        'validating_rewards',
        'validating_penalties',
        'total_online_validator_rewards',
        'total_priority_fee_to_validators',
        'source_reward',
        'target_reward',
        'head_reward',
        'block_proposer_reward',
        'sync_reward',
        'whistleblower_rewards'
    ]
    df[[reward + '_eth' for reward in validator_rewards]] = df[validator_rewards] / constants.gwei

    # Convert validator penalties from Gwei to ETH
    validator_penalties = ['validating_penalties', 'amount_slashed']
    df[[penalty + '_eth' for penalty in validator_penalties]] = df[validator_penalties] / constants.gwei

    # Calculate cumulative revenue and profit yields
    df["daily_revenue_yields_pct"] = df["total_revenue_yields_pct"] / (constants.epochs_per_year / df['dt'])
    df["cumulative_revenue_yields_pct"] = df.groupby('subset')["daily_revenue_yields_pct"].transform('cumsum')
    df["daily_profit_yields_pct"] = df["total_profit_yields_pct"] / (constants.epochs_per_year / df['dt'])
    df["cumulative_profit_yields_pct"] = df.groupby('subset')["daily_profit_yields_pct"].transform('cumsum')

    # Drop the initial state for plotting
    if drop_timestep_zero:
        df = df.drop(df.query('timestep == 0').index)

    return df
