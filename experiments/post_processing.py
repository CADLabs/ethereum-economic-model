import pandas as pd
from model.parameters import validator_types


def post_process(df: pd.DataFrame):
    df[[validator.type + '_hardware_costs' for validator in validator_types]] = df.apply(lambda row: list(row.validator_hardware_costs), axis=1, result_type='expand')
    df[[validator.type + '_cloud_costs' for validator in validator_types]] = df.apply(lambda row: list(row.validator_cloud_costs), axis=1, result_type='expand')
    df[[validator.type + '_third_party_costs' for validator in validator_types]] = df.apply(lambda row: list(row.validator_third_party_costs), axis=1, result_type='expand')
    
    return df
