import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd
pd.options.plotting.backend = "plotly"

import model.constants as constants
from model.parameters import validator_types


def plot_validator_rewards(df):
    validator_rewards = ['source_reward_eth', 'target_reward_eth', 'head_reward_eth', 'block_proposer_reward_eth', 'sync_reward_eth']
    
    return df.plot.area(
        x='timestamp', 
        y=validator_rewards,
        labels={
            "timestamp": "Date",
            "value": "Reward (ETH)",
        },
        height=800
    )


def plot_validator_environment_yields(df):
    validator_profit_yields = [validator.type + '_profit_yields' for validator in validator_types]
    df[validator_profit_yields] = df[validator_profit_yields] * 100

    return df.plot(
        x='eth_price',
        y=(validator_profit_yields + ['total_profit_yields_pct']),
        title=f'Net Yields of Validator Environments @ {df.eth_staked.iloc[0]} ETH Staked',
        height=800
    )


def plot_revenue_yields_vs_network_inflation(df):
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    df_subset_0 = df.query("subset == 0")
    df_subset_1 = df.query("subset == 1")

    # Add traces
    fig.add_trace(
        go.Scatter(x=df_subset_0.timestamp, y=df_subset_0.total_revenue_yields_pct, name="Revenue yields (%)"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df_subset_0.timestamp, y=df_subset_0.total_profit_yields_pct, name=f"Net yields @ {df_subset_0.eth_price.iloc[0]} $/ETH (%)"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df_subset_1.timestamp, y=df_subset_1.total_profit_yields_pct, name=f"Net yields @ {df_subset_1.eth_price.iloc[0]} $/ETH (%)"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df_subset_0.timestamp, y=df_subset_0.supply_inflation_pct, name="ETH Supply inflation (%)"),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(
        title_text="Revenue Yields vs. Network Inflation",
        height=800
    )

    # Set x-axis title
    fig.update_xaxes(title_text="Timestamp")

    # Set y-axes titles
    fig.update_yaxes(title_text="Revenue Yields", secondary_y=False)
    fig.update_yaxes(title_text="Network Inflation Rate (Annualized)", secondary_y=True)

    fig.show()
