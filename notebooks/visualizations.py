import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd
pd.options.plotting.backend = "plotly"

import inspect
from IPython.display import Code

from pygments.formatters import HtmlFormatter
from IPython.core.display import HTML

import model.constants as constants
from model.parameters import parameters, validator_types


def inspect_module(module):
    formatter = HtmlFormatter()
    display(HTML(f'<style>{ formatter.get_style_defs(".highlight") }</style>'))

    return Code(inspect.getsource(module), language='python')


def plot_validating_rewards(df):
    validator_rewards = ['source_reward_eth', 'target_reward_eth', 'head_reward_eth', 'block_proposer_reward_eth', 'sync_reward_eth']
    
    return df.plot.area(
        x='timestamp', 
        y=validator_rewards,
        title="Validating Rewards",
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
        go.Scatter(x=df_subset_0.eth_staked, y=df_subset_0.total_revenue_yields_pct, name="Revenue yields (%)"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df_subset_0.eth_staked, y=df_subset_0.total_profit_yields_pct, name=f"Net yields @ {df_subset_0.eth_price.iloc[0]} $/ETH (%)"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df_subset_1.eth_staked, y=df_subset_1.total_profit_yields_pct, name=f"Net yields @ {df_subset_1.eth_price.iloc[0]} $/ETH (%)"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df_subset_0.eth_staked, y=df_subset_0.supply_inflation_pct, name="ETH Supply inflation (%)"),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(
        title_text="Revenue Yields vs. Network Inflation",
        height=800
    )

    # Set x-axis title
    fig.update_xaxes(title_text="ETH Staked (Ether)")

    # Set y-axes titles
    fig.update_yaxes(title_text="Revenue Yields", secondary_y=False)
    fig.update_yaxes(title_text="Network Inflation Rate (Annualized)", secondary_y=True)

    return fig

    
def plot_validator_environment_yield_contour(x, y, z):
    fig = go.Figure(data=[
        go.Contour(
            x=x, y=y, z=z,
            line_smoothing=0.85
        )
    ])

    fig.update_layout(
        title="Counter Plot of Annualized Validator Yield over ETH Price vs. ETH Staked",
        autosize=False,
        width=1000, height=800,
    )
    fig.update_yaxes(title_text="ETH Staked (Ether)")
    fig.update_xaxes(title_text="ETH Price ($/Ether)")

    return fig


def plot_validator_environment_yield_surface(x, y, z):
    fig = go.Figure(data=[go.Surface(x=x, y=y, z=z)])

    fig.update_traces(contours_z=dict(
        show=True,
        usecolormap=True,
        project_z=True
    ))

    fig.update_layout(
        title="Surface Plot of Annualized Validator Yield over ETH Price vs. ETH Staked",
        autosize=False,
        width=1000, height=800,
        margin=dict(l=65, r=50, b=65, t=90),
        scene={
            "xaxis": {"title" : { "text": "ETH Price ($/Ether)" }},
            "yaxis": {"type": "log", "title" : { "text": "ETH Staked (Ether; Logarithmic axis)" }},
            "zaxis": {"title" : { "text": "Yield (%)" }},
        }
    )

    return fig


def plot_eth_supply_over_all_phases(df):
    date_start = parameters["date_start"][0]
    date_eip1559 = parameters["date_eip1559"][0]
    date_merge = parameters["date_merge"][0]
    date_end = df.index[0]

    fig = df.plot(y='eth_supply', title='ETH Supply', width=1000, height=600)

    fig.add_shape(
        type="rect",
        xref="x",
        yref="paper",
        x0=date_start,
        y0=0,
        x1=date_eip1559,
        y1=1,
        line=dict(color="rgba(0,0,0,0)",width=3,),
        fillcolor="rgba(0,0,0,0.3)",
        layer='below'
    )

    fig.add_shape(
        type="rect",
        xref="x",
        yref="paper",
        x0=date_eip1559,
        y0=0,
        x1=date_merge,
        y1=1,
        line=dict(color="rgba(0,0,0,0)",width=3,),
        fillcolor="rgba(0,0,0,0.2)",
        layer='below'
    )

    fig.add_shape(
        type="rect",
        xref="x",
        yref="paper",
        x0=date_merge,
        y0=0,
        x1=date_end,
        y1=1,
        line=dict(color="rgba(0,0,0,0)",width=3,),
        fillcolor="rgba(0,0,0,0.1)",
        layer='below'
    )

    fig.add_annotation(
        x=date_start, y=df['eth_supply'][0],
        text="Today",
        showarrow=True,
        arrowhead=1
    )

    fig.add_annotation(
        x=date_eip1559, y=df.loc[date_eip1559.strftime("%Y-%m-%d")]['eth_supply'][0],
        text="EIP1559 Enabled",
        showarrow=True,
        arrowhead=1
    )

    fig.add_annotation(
        x=date_merge, y=df.loc[date_merge.strftime("%Y-%m-%d")]['eth_supply'][0],
        text="The Merge",
        showarrow=True,
        arrowhead=1,
    )

    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )
    
    fig.update_yaxes(title_text="ETH Supply (Ether)")
    fig.update_xaxes(title_text="Timestamp")

    return fig
    

def plot_eth_supply_inflation_over_all_phases(df):
    date_start = parameters["date_start"][0]
    date_eip1559 = parameters["date_eip1559"][0]
    date_merge = parameters["date_merge"][0]
    date_end = df.index[0]
    
    fig = df.plot(x='timestamp', y='supply_inflation_pct', title='Supply Inflation')

    fig.add_annotation(
        x=date_start, y=df['supply_inflation_pct'][0],
        text="Today",
        showarrow=True,
        arrowhead=1
    )

    fig.add_annotation(
        x=date_eip1559, y=df.loc[date_eip1559.strftime("%Y-%m-%d")]['supply_inflation_pct'][0],
        text="EIP1559 Enabled",
        showarrow=True,
        arrowhead=1
    )

    fig.add_annotation(
        x=date_merge, y=df.loc[date_merge.strftime("%Y-%m-%d")]['supply_inflation_pct'][0],
        text="The Merge",
        showarrow=True,
        arrowhead=1,
    )

    return fig

    
def plot_eth_staked_over_all_phases(df):
    date_start = parameters["date_start"][0]
    date_eip1559 = parameters["date_eip1559"][0]
    date_merge = parameters["date_merge"][0]
    date_end = df.index[0]
    
    fig = df.plot(x='timestamp', y='eth_staked', title='ETH Staked')

    fig.add_annotation(
        x=date_start, y=df['eth_staked'][0],
        text="Today",
        showarrow=True,
        arrowhead=1
    )

    fig.add_annotation(
        x=date_eip1559, y=df.loc[date_eip1559.strftime("%Y-%m-%d")]['eth_staked'][0],
        text="EIP1559 Enabled",
        showarrow=True,
        arrowhead=1
    )

    fig.add_annotation(
        x=date_merge, y=df.loc[date_merge.strftime("%Y-%m-%d")]['eth_staked'][0],
        text="The Merge",
        showarrow=True,
        arrowhead=1,
    )

    return fig
