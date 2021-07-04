import os
import pandas as pd
import model.constants as constants
from model.simulation_configuration import DELTA_TIME


# Fetch CSV file relative to current file path
file_ether_price_csv = os.path.join(os.path.dirname(__file__), "ether_price.csv")
file_ether_supply_csv = os.path.join(os.path.dirname(__file__), "ether_supply.csv")

# Calculate mean, min, max ETH price over last 12 months from Etherscan
df_ether_price = pd.read_csv(file_ether_price_csv)
df_ether_price = df_ether_price.set_index(['Date(UTC)'], drop=False)
df_ether_price = df_ether_price.loc['7/3/2020':'7/3/2021']
eth_price_mean = df_ether_price.Value.mean()
eth_price_min = df_ether_price.Value.min()
eth_price_max = df_ether_price.Value.max()


# Calculate historical Ether supply inflation
df_ether_supply = pd.read_csv(file_ether_supply_csv)
df_ether_supply['timestamp'] = pd.to_datetime(df_ether_supply['UnixTimeStamp'], unit='s')
df_ether_supply = df_ether_supply.rename(columns={"Value": "eth_supply"})
df_ether_supply = df_ether_supply[['timestamp','eth_supply']]
df_ether_supply = df_ether_supply.set_index('timestamp', drop=False)
df_ether_supply['supply_inflation'] = \
    constants.epochs_per_year * (df_ether_supply['eth_supply'].shift(-1) - df_ether_supply['eth_supply']) \
    / (df_ether_supply['eth_supply'] * DELTA_TIME)
df_ether_supply = df_ether_supply.fillna(method='bfill')
df_ether_supply['supply_inflation_pct'] = df_ether_supply['supply_inflation'] * 100
