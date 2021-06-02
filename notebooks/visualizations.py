import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

import pandas as pd
pd.options.plotting.backend = "plotly"

import inspect
from IPython.display import Code

from pygments.formatters import HtmlFormatter
from IPython.core.display import HTML

import model.constants as constants
from model.parameters import parameters, validator_environments


def inspect_module(module):
    formatter = HtmlFormatter()
    display(HTML(f'<style>{ formatter.get_style_defs(".highlight") }</style>'))

    return Code(inspect.getsource(module), language='python')


def plot_validating_rewards(df):
    validator_rewards = ['source_reward_eth', 'target_reward_eth', 'head_reward_eth', 'block_proposer_reward_eth', 'sync_reward_eth']
    
    fig = df.plot.area(
        x='timestamp', 
        y=validator_rewards,
        title="Validating Rewards",
        labels={
            "timestamp": "Date",
            "value": "Reward (ETH)",
        },
        height=800
    )
    
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )
    
    return fig


def plot_validating_rewards_pie_chart(df, with_tips=False):
    if with_tips:
        title = 'Validating Rewards with Tips'
        validator_rewards = df.iloc[-1][['total_tips_to_validators_eth', 'source_reward_eth', 'target_reward_eth', 'head_reward_eth', 'block_proposer_reward_eth', 'sync_reward_eth']].to_dict()
        names = ["Tips", "Source Reward", "Target Reward", "Head Reward", "Block Proposer Reward", "Sync Reward"]
    else:
        title = 'Validating Rewards'
        validator_rewards = df.iloc[-1][['source_reward_eth', 'target_reward_eth', 'head_reward_eth', 'block_proposer_reward_eth', 'sync_reward_eth']].to_dict()
        names = ["Source Reward", "Target Reward", "Head Reward", "Block Proposer Reward", "Sync Reward"]

    fig = px.pie(df, values=validator_rewards.values(), names=names, title=title, height=600)

    fig.for_each_trace(
        lambda trace: trace.update(
            textinfo='label+percent',
            insidetextorientation='radial',
            marker=dict(line=dict(color='#000000', width=2))
        ),
    )

    fig.show()


def plot_validator_environment_yields(df):
    validator_profit_yields_pct = [validator.type + '_profit_yields_pct' for validator in validator_environments]

    return df.plot(
        x='eth_price',
        y=(validator_profit_yields_pct + ['total_profit_yields_pct']),
        title=f'Net Yields of Validator Environments @ {df.eth_staked.iloc[0]} ETH Staked',
        height=800
    )


def plot_three_region_yield_analysis(fig_df):
    fig = fig_df.plot(
        x='eth_price',
        y=['total_revenue_yields_pct','total_profit_yields_pct'],
        title=f'Three Region Yield Analysis @ {fig_df.eth_staked.iloc[0]} ETH Staked',
        height=800
    )

    fig.add_annotation(
        x=fig_df['eth_price'].min() + 100, y=fig_df['total_revenue_yields_pct'].max(),
        text="Cliff",
        showarrow=False,
        yshift=10
    )

    fig.add_annotation(
        x=fig_df['eth_price'].median(), y=fig_df['total_revenue_yields_pct'].max(),
        text="Economics of Scale",
        showarrow=False,
        yshift=10
    )

    fig.add_annotation(
        x=fig_df['eth_price'].max() - 100, y=fig_df['total_revenue_yields_pct'].max(),
        text="Stability",
        showarrow=False,
        yshift=10
    )

    return fig


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

    
def plot_validator_environment_yield_contour(df):
    grouped = df.groupby(["eth_price", "eth_staked"]).last()["total_profit_yields_pct"]

    x = df.groupby(["run"]).first()["eth_price"].unique()
    y = df.groupby(["run"]).first()["eth_staked"].unique()
    z = []

    for eth_staked in y:
        row = []
        for eth_price in x:
            z_value = grouped[eth_price][eth_staked]
            row.append(z_value)
        z.append(row)
    
    fig = go.Figure(data=[
        go.Contour(
            x=x, y=y, z=z,
            line_smoothing=0.85,
            colorbar=dict(
                title='Yield (%)',
                titleside='right',
                titlefont=dict(size=14)
            )
        )
    ])

    fig.update_layout(
        title="Contour Plot of Annualized Validator Yield over ETH Price vs. ETH Staked",
        autosize=False,
        width=1000, height=800,
    )
    fig.update_yaxes(title_text="ETH Staked (ETH)")
    fig.update_xaxes(title_text="ETH Price ($/ETH)")

    return fig


def plot_revenue_net_yield_spread(df):
    grouped = df.groupby(["eth_price", "eth_staked"]).last()["revenue_net_yield_spread_pct"]

    x = df.groupby(["run"]).first()["eth_price"].unique()
    y = df.groupby(["run"]).first()["eth_staked"].unique()
    z = []

    for eth_staked in y:
        row = []
        for eth_price in x:
            z_value = grouped[eth_price][eth_staked]
            row.append(z_value)
        z.append(row)
    
    fig = go.Figure(data=[
        go.Contour(
            x=x, y=y, z=z,
            line_smoothing=0.85,
            contours=dict(
                showlabels = True, # show labels on contours
                labelfont = dict( # label font properties
                    size = 12,
                    color = 'white',
                )
            ),
            colorbar=dict(
                title='Spread (%)',
                titleside='right',
                titlefont=dict(size=14)
            )
        )
    ])

    fig.update_layout(
        title="Contour Plot of Revenue-Net Yield Spread over ETH Price vs. ETH Staked",
        autosize=False,
        width=1000, height=800,
    )
    fig.update_yaxes(title_text="ETH Staked (ETH)")
    fig.update_xaxes(title_text="ETH Price ($/ETH)")

    return fig


def plot_validator_environment_yield_surface(df):
    grouped = df.groupby(["eth_price", "eth_staked"]).last()["total_profit_yields_pct"]

    x = df.groupby(["run"]).first()["eth_price"].unique()
    y = df.groupby(["run"]).first()["eth_staked"].unique()
    z = []

    for eth_staked in y:
        row = []
        for eth_price in x:
            z_value = grouped[eth_price][eth_staked]
            row.append(z_value)
        z.append(row)
        
    fig = go.Figure(data=[go.Surface(
        x=x, y=y, z=z,
        colorbar=dict(
            title='Yield (%)',
            titleside='right',
            titlefont=dict(size=14)
        )
    )])

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
            "xaxis": {"title" : { "text": "ETH Price ($/ETH)" }, "type": "log",},
            "yaxis": {"title" : { "text": "ETH Staked (ETH; Logarithmic axis)" }},
            "zaxis": {"title" : { "text": "Yield (%)" }},
        }
    )

    return fig


def plot_eth_supply_over_all_phases(df):
    date_start = parameters["date_start"][0]
    date_eip1559 = parameters["date_eip1559"][0]
    date_merge = parameters["date_merge"][0]
    date_end = df.index[0]

    fig = df.plot(y='eth_supply', title='ETH Supply', height=600)

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
    
    fig = df.plot(x='timestamp', y='supply_inflation_pct', title='ETH Supply Inflation', height=600)

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
    
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )
    
    fig.update_yaxes(title_text="ETH Supply Inflation (%/year)")
    fig.update_xaxes(title_text="Timestamp")

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
    
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )

    return fig
