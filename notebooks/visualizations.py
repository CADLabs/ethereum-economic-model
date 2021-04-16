import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd
pd.options.plotting.backend = "plotly"

from model.parameters import validator_types


def plot_validator_rewards(df):
    df.plot.area(x='timestep', y=['source_reward', 'target_reward', 'head_reward', 'block_proposer_reward', 'sync_reward'])


def plot_validator_environment_yields(df):
    # validator_profit_yields = [validator.type + '_profit_yields' for validator in validator_types]
    # df[validator_profit_yields] = df[validator_profit_yields] * 100

    # df.plot(x='timestep', y=(validator_profit_yields + ['total_profit_yields_pct']), title='Net Yields of Validator Environments')

    df.plot.area(x='timestep', y=['source_reward', 'target_reward', 'head_reward', 'block_proposer_reward', 'sync_reward'])



def plot_revenue_yields_vs_network_inflation(df):
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    df_subset_0 = df.query("subset == 0")
    df_subset_1 = df.query("subset == 1")

    # Add traces
    fig.add_trace(
        go.Scatter(x=df_subset_0.timestep, y=df_subset_0.total_revenue_yields_pct, name="Revenue yields (%)"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df_subset_0.timestep, y=df_subset_0.total_profit_yields_pct, name="Net yields @ 25 (%)"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df_subset_1.timestep, y=df_subset_1.total_profit_yields_pct, name="Net yields @ 1500 (%)"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df_subset_0.timestep, y=df_subset_0.supply_inflation_pct, name="ETH Supply inflation (%)"),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(
        title_text="Revenue Yields vs. Network Inflation"
    )

    # Set x-axis title
    fig.update_xaxes(title_text="Epochs")

    # Set y-axes titles
    fig.update_yaxes(title_text="Revenue Yields", secondary_y=False)
    fig.update_yaxes(title_text="Network Inflation Rate (Annualized)", secondary_y=True)

    fig.show()
