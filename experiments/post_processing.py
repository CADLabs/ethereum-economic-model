import pandas as pd
from model.types import validator_types


def post_process(df: pd.DataFrame):
    df[[type + '_hardware_costs' for type in validator_types]] = df.apply(lambda row: list(row.validator_hardware_costs), axis=1, result_type='expand')
    df[[type + '_cloud_costs' for type in validator_types]] = df.apply(lambda row: list(row.validator_cloud_costs), axis=1, result_type='expand')
    df[[type + '_third_party_costs' for type in validator_types]] = df.apply(lambda row: list(row.validator_third_party_costs), axis=1, result_type='expand')
    
    return df
