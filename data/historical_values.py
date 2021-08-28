import os
import pandas as pd
import model.constants as constants
from experiments.simulation_configuration import DELTA_TIME
from model.types import  Gwei_per_Gas


# Set 12 month window
window_start = '7/3/2020'
window_end = '7/3/2021'

# Fetch CSV file relative to current file path
file_ether_price_csv = os.path.join(os.path.dirname(__file__), "ether_price.csv")
file_ether_supply_csv = os.path.join(os.path.dirname(__file__), "ether_supply.csv")
file_ether_avg_gas_price = os.path.join(os.path.dirname(__file__), "ether_avg_gas_price.csv")
file_ether_block_rewards = os.path.join(os.path.dirname(__file__), "ether_block_rewards.csv")

# Calculate mean, min, max ETH price over last 12 months from Etherscan
df_ether_price = pd.read_csv(file_ether_price_csv)
df_ether_price = df_ether_price.set_index(['Date(UTC)'], drop=False)
df_ether_price = df_ether_price.loc[window_start:window_end]
eth_price_mean = df_ether_price.Value.mean()
eth_price_min = df_ether_price.Value.min()
eth_price_max = df_ether_price.Value.max()

# Calculate Ethereum average gas price over last 12 months from Etherscan
df_gas_price = pd.read_csv(file_ether_avg_gas_price)
df_gas_price = df_gas_price.set_index(['Date(UTC)'], drop=False)
df_gas_price = df_gas_price.loc[window_start:window_end]
eth_gas_price_median: Gwei_per_Gas = df_gas_price['Value (Wei)'].median() / constants.gwei

# Calculate Ethereum average block rewards over last 12 months from Etherscan
df_block_rewards = pd.read_csv(file_ether_block_rewards)
df_block_rewards = df_block_rewards.set_index(['Date(UTC)'], drop=False)
df_block_rewards = df_block_rewards.loc[window_start:window_end]
eth_block_rewards_mean = df_block_rewards['Value'].mean()

# Calculate historical Ether supply inflation
df_ether_supply = pd.read_csv(file_ether_supply_csv)
df_ether_supply['timestamp'] = pd.to_datetime(df_ether_supply['UnixTimeStamp'], unit='s')
df_ether_supply = df_ether_supply.rename(columns={"Value": "eth_supply"})
df_ether_supply = df_ether_supply[['timestamp','eth_supply']]
df_ether_supply = df_ether_supply.set_index('timestamp', drop=False)
df_ether_supply['supply_inflation'] = \
    constants.epochs_per_year * (df_ether_supply['eth_supply'].shift(-1) - df_ether_supply['eth_supply']) \
    / (df_ether_supply['eth_supply'] * DELTA_TIME)
df_ether_supply['supply_inflation_pct'] = df_ether_supply['supply_inflation'] * 100
df_ether_supply['supply_inflation_pct_rolling'] = df_ether_supply['supply_inflation_pct'].rolling(14).mean()
df_ether_supply = df_ether_supply.fillna(method='bfill')
