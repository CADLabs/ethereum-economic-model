import pandas as pd
from functools import partial
from radcad.core import apply_state_update_blocks, generate_parameter_sweep

from model.parameters import validator_types, parameters
from model.state_update_blocks import post_processing_blocks


def post_process(df: pd.DataFrame):
    df[[validator.type + '_hardware_costs' for validator in validator_types]] = df.apply(lambda row: list(row.validator_hardware_costs), axis=1, result_type='expand').astype('float64')
    df[[validator.type + '_cloud_costs' for validator in validator_types]] = df.apply(lambda row: list(row.validator_cloud_costs), axis=1, result_type='expand').astype('float64')
    df[[validator.type + '_third_party_costs' for validator in validator_types]] = df.apply(lambda row: list(row.validator_third_party_costs), axis=1, result_type='expand').astype('float64')

    df[[validator.type + '_revenue_yields' for validator in validator_types]] = df.apply(lambda row: list(row.validator_revenue_yields), axis=1, result_type='expand').astype('float64')
    df[[validator.type + '_profit_yields' for validator in validator_types]] = df.apply(lambda row: list(row.validator_profit_yields), axis=1, result_type='expand').astype('float64')

    df['supply_inflation_pct'] = df['supply_inflation'] * 100
    df['total_revenue_yields_pct'] = df['total_revenue_yields'] * 100
    df['total_profit_yields_pct'] = df['total_profit_yields'] * 100

    df = df.drop(df.query('timestep == 0').index)

    return df
