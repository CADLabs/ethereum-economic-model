import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from ipywidgets import widgets

pd.options.plotting.backend = "plotly"

import inspect
from IPython.display import Code

from pygments.formatters import HtmlFormatter
from IPython.core.display import HTML

import model.constants as constants
from model.system_parameters import parameters, validator_environments

import experiments.notebooks.plotly_theme
from experiments.notebooks.plotly_theme import cadlabs_colors


legend_state_variable_name_mapping = {
    'timestamp': 'Date',
    'eth_price': 'ETH Price',
    'eth_staked': 'ETH Staked',
    'eth_supply': 'ETH Supply',
    'source_reward_eth': 'Source Reward',
    'target_reward_eth': 'Target Reward',
    'head_reward_eth': 'Head Reward',
    'block_proposer_reward_eth': 'Block Proposer Reward',
    'sync_reward_eth': 'Sync Reward',
    'total_tips_to_validators_eth': 'Tips',
    'supply_inflation_pct': 'ETH Supply inflation',
    'total_revenue_yields_pct': 'Total Revenue Yields',
    'total_profit_yields_pct': 'Total Profit Yields',
    'revenue_profit_yield_spread_pct': 'Revenue-Profit Yield Spread',
    **dict([(validator.type + '_profit_yields_pct', f'{validator.type} Profit Yields') for validator in
            validator_environments])
}

axis_state_variable_name_mapping = {
    **legend_state_variable_name_mapping,
    'eth_price': 'ETH Price (USD/ETH)',
    'eth_staked': 'ETH Staked (ETH)',
    'eth_supply': 'ETH Supply (ETH)',
}


def inspect_module(module):
    formatter = HtmlFormatter()
    display(HTML(f'<style>{formatter.get_style_defs(".highlight")}</style>'))

    return Code(inspect.getsource(module), language='python')


def update_legend_names(fig, name_mapping=legend_state_variable_name_mapping):
    for i, dat in enumerate(fig.data):
        for elem in dat:
            if elem == 'name':
                try:
                    fig.data[i].name = name_mapping[fig.data[i].name]
                except KeyError:
                    continue
    return (fig)


def update_axis_names(fig, name_mapping=axis_state_variable_name_mapping):
    def update_axis_name(axis):
        title = axis['title']
        text = title['text']
        updated_text = name_mapping.get(text, text)
        title.update({'text': updated_text})

    fig.for_each_xaxis(lambda ax: update_axis_name(ax))
    fig.for_each_yaxis(lambda ax: update_axis_name(ax))
    return fig


def apply_plotly_standards(
        fig,
        title=None,
        xaxis_title=None,
        yaxis_title=None,
        legend_title=None,
        axis_state_variable_name_mapping_override={},
        legend_state_variable_name_mapping_override={},
):
    update_axis_names(
        fig,
        {**axis_state_variable_name_mapping, **axis_state_variable_name_mapping_override},
    )
    update_legend_names(
        fig,
        {**legend_state_variable_name_mapping, **legend_state_variable_name_mapping_override},
    )

    if title:
        fig.update_layout(title=title)
    if xaxis_title:
        fig.update_layout(xaxis_title=xaxis_title)
    if yaxis_title:
        fig.update_layout(yaxis_title=yaxis_title)
    if legend_title:
        fig.update_layout(legend_title=legend_title)

    return fig


def plot_validating_rewards(df):
    validating_rewards = [
        'source_reward_eth',
        'target_reward_eth',
        'head_reward_eth',
        'block_proposer_reward_eth',
        'sync_reward_eth',
    ]

    fig = px.area(
        df,
        x='timestamp',
        y=list(validating_rewards),
        title="Validating Rewards",
        height=800
    )

    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True
            ),
            type="date"
        ),
    )

    update_legend_names(fig)

    fig.update_layout(
        title="Validating Rewards",
        xaxis_title="Date",
        yaxis_title="Reward (ETH)",
        legend_title="",
    )

    return fig


def plot_validating_rewards_pie_chart(df, with_tips=False):
    if with_tips:
        title = 'Validating Rewards with Tips'
        validator_rewards = df.iloc[-1][
            ['total_tips_to_validators_eth', 'source_reward_eth', 'target_reward_eth', 'head_reward_eth',
             'block_proposer_reward_eth', 'sync_reward_eth']].to_dict()
        names = ["Tips", "Source Reward", "Target Reward", "Head Reward", "Block Proposer Reward", "Sync Reward"]
    else:
        title = 'Validating Rewards'
        validator_rewards = df.iloc[-1][
            ['source_reward_eth', 'target_reward_eth', 'head_reward_eth', 'block_proposer_reward_eth',
             'sync_reward_eth']].to_dict()
        names = ["Source Reward", "Target Reward", "Head Reward", "Block Proposer Reward", "Sync Reward"]

    fig = px.pie(df, values=validator_rewards.values(), names=names)

    fig.for_each_trace(
        lambda trace: trace.update(
            textinfo='label+percent',
            insidetextorientation='radial',
            marker=dict(line=dict(color='#000000', width=2))
        ),
    )

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Reward (ETH)",
        height=600,
        showlegend=False,
    )

    return fig


def plot_revenue_profit_yields_over_eth_staked(df):
    fig = go.Figure()

    df_subset_0 = df.query("subset == 0")
    df_subset_1 = df.query("subset == 1")

    # Add traces
    fig.add_trace(
        go.Scatter(x=df_subset_0.eth_staked, y=df_subset_0.total_revenue_yields_pct, name='Revenue Yields'),
    )

    fig.add_trace(
        go.Scatter(x=df_subset_0.eth_staked, y=df_subset_0.total_profit_yields_pct,
                   name=f"Profit Yields @ {df_subset_0.eth_price.iloc[0]:.0f} USD/ETH"),
    )

    fig.add_trace(
        go.Scatter(x=df_subset_1.eth_staked, y=df_subset_1.total_profit_yields_pct,
                   name=f"Profit Yields @ {df_subset_1.eth_price.iloc[0]:.0f} USD/ETH"),
    )

    update_legend_names(fig)

    fig.update_layout(
        title="Revenue and Profit Yields Over ETH Staked",
        xaxis_title="ETH Staked (ETH)",
        # yaxis_title="",
        legend_title="",
    )

    # Set secondary y-axes titles
    fig.update_yaxes(title_text="Yield (%/year)")

    return fig


def plot_revenue_profit_yields_over_eth_price(df):
    fig = go.Figure()

    df_subset_0 = df.query("subset == 0")
    df_subset_1 = df.query("subset == 1")

    # Add traces
    fig.add_trace(
        go.Scatter(x=df_subset_0.eth_price, y=df_subset_0.total_revenue_yields_pct, name='Revenue Yields'),
    )

    fig.add_trace(
        go.Scatter(x=df_subset_0.eth_price, y=df_subset_0.total_profit_yields_pct,
                   name=f"Profit Yields @ {df_subset_0.eth_staked.iloc[0]:.0f} ETH"),
    )

    fig.add_trace(
        go.Scatter(x=df_subset_1.eth_price, y=df_subset_1.total_profit_yields_pct,
                   name=f"Profit Yields @ {df_subset_1.eth_staked.iloc[0]:.0f} ETH"),
    )

    update_legend_names(fig)

    fig.update_layout(
        title="Revenue and Profit Yields Over ETH Price",
        xaxis_title="ETH Price (USD/ETH)",
        # yaxis_title="",
        legend_title="",
    )

    # Set secondary y-axes titles
    fig.update_yaxes(title_text="Yield (%/year)")

    return fig


def plot_validator_environment_yields(df):
    validator_profit_yields_pct = [validator.type + '_profit_yields_pct' for validator in validator_environments]

    fig = df.plot(
        x='eth_price',
        y=(validator_profit_yields_pct + ['total_profit_yields_pct']),
        facet_col='subset',
        facet_col_wrap=2,
        facet_col_spacing=0.05
    )

    fig.for_each_annotation(lambda a: a.update(text=f"ETH Staked = {df.query(f'subset == {a.text.split(chr(61))[1]}').eth_staked.iloc[0]:.0f} ETH"))

    fig.update_layout(
        title=f'Profit Yields of Validator Environments',
        xaxis_title="ETH Price (USD/ETH)",
        yaxis_title="Profit Yields (%/year)",
        legend_title="",
    )

    fig.for_each_xaxis(lambda x: x['title'].update({'text': "ETH Price (USD/ETH)"}))
    fig.update_yaxes(matches=None)
    fig.update_yaxes(showticklabels=True)

    update_legend_names(fig)

    return fig


def plot_three_region_yield_analysis(fig_df):
    fig = fig_df.plot(
        x='eth_price',
        y=['total_revenue_yields_pct', 'total_profit_yields_pct'],
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

    update_legend_names(fig)

    fig.update_layout(
        title=f"Three Region Yield Analysis @ {fig_df.eth_staked.iloc[0]} ETH Staked",
        xaxis_title="ETH Price (USD/ETH)",
        yaxis_title="Revenue Yields (%/year)",
        legend_title="",
    )

    return fig


def plot_revenue_yields_vs_network_inflation(df):
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    df_subset_0 = df.query("subset == 0")
    df_subset_1 = df.query("subset == 1")

    # Add traces
    fig.add_trace(
        go.Scatter(x=df_subset_0.eth_staked, y=df_subset_0.total_revenue_yields_pct, name='Revenue Yields'),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df_subset_0.eth_staked, y=df_subset_0.total_profit_yields_pct,
                   name=f"Profit Yields @ {df_subset_0.eth_price.iloc[0]} USD/ETH"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df_subset_1.eth_staked, y=df_subset_1.total_profit_yields_pct,
                   name=f"Profit Yields @ {df_subset_1.eth_price.iloc[0]} USD/ETH"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df_subset_0.eth_staked, y=df_subset_0.supply_inflation_pct, name='Network Inflation Rate'),
        secondary_y=True,
    )

    update_legend_names(fig)

    fig.update_layout(
        title="Revenue Yields vs. Network Inflation",
        xaxis_title="ETH Staked (ETH)",
        # yaxis_title="",
        legend_title="",
    )

    # Set secondary y-axes titles
    fig.update_yaxes(title_text="Revenue Yields (%/year)", secondary_y=False)
    fig.update_yaxes(title_text="Network Inflation Rate (%/year)", secondary_y=True)

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
            colorscale=cadlabs_colors,
            colorbar=dict(
                title='Profit Yield (%/year)',
                titleside='right',
                titlefont=dict(size=14)
            )
        )
    ])

    update_legend_names(fig)

    fig.update_layout(
        title="Profit Yield Over ETH Price vs. ETH Staked",
        xaxis_title="ETH Price (USD/ETH)",
        yaxis_title="ETH Staked (ETH)",
        width=1000,
        legend_title="",
        autosize=False,
    )

    return fig


def plot_revenue_profit_yield_spread(df):
    grouped = df.groupby(["eth_price", "eth_staked"]).last()["revenue_profit_yield_spread_pct"]

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
                showlabels=True,  # show labels on contours
                labelfont=dict(  # label font properties
                    size=12,
                    color='white',
                )
            ),
            colorbar=dict(
                title='Spread (%/year)',
                titleside='right',
                titlefont=dict(size=14)
            ),
            colorscale=cadlabs_colors
        )
    ])

    update_legend_names(fig)

    fig.update_layout(
        title="Revenue-Profit Yield Spread Over ETH Price vs. ETH Staked",
        xaxis_title="ETH Price (USD/ETH)",
        yaxis_title="ETH Staked (ETH)",
        width=1000,
        legend_title="",
        autosize=False,
    )

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
        ),
        colorscale=cadlabs_colors
    )])

    fig.update_traces(contours_z=dict(
        show=True,
        usecolormap=True,
        project_z=True
    ))

    update_legend_names(fig)

    fig.update_layout(
        title="Profit Yields over ETH Price vs. ETH Staked",
        autosize=False,
        width=1000,
        legend_title="",
        margin=dict(l=65, r=50, b=65, t=90),
        scene={
            "xaxis": {"title": {"text": "ETH Price (USD/ETH)"}, "type": "log", },
            "yaxis": {"title": {"text": "ETH Staked (ETH; Logarithmic axis)"}},
            "zaxis": {"title": {"text": "Profit Yield (%/year)"}},
        }
    )

    return fig

def fig_add_stage_vrects(df, fig):
    date_start = parameters["date_start"][0]
    date_eip1559 = parameters["date_eip1559"][0]
    date_pos = parameters["date_pos"][0]
    date_end = df.index[-1]

    fig.add_vrect(x0=date_start, x1=date_eip1559, row="all", col=1,
                  # annotation_text="Beacon Chain",
                  # annotation_position="top left",
                  layer="below",
                  fillcolor="gray", opacity=0.5, line_width=0)

    fig.add_vrect(x0=date_eip1559, x1=date_pos, row="all", col=1,
                  # annotation_text="EIP1559 Enabled",
                  # annotation_position="top left",
                  layer="below",
                  fillcolor="gray", opacity=0.25, line_width=0)

    fig.add_vrect(x0=date_pos, x1=date_end, row="all", col=1,
                  # annotation_text="Proof of Stake",
                  # annotation_position="top left",
                  layer="below",
                  fillcolor="gray", opacity=0.1, line_width=0)
    return fig


def fig_add_stage_markers(df, column, fig, secondary_y=None):
    date_start = parameters["date_start"][0]
    date_eip1559 = parameters["date_eip1559"][0]
    date_pos = parameters["date_pos"][0]

    fig.add_trace(
        go.Scatter(
            mode="markers", x=[date_start], y=[df[column][0]],
            marker_symbol=["diamond"],
            # marker_line_color="midnightblue", marker_color="lightskyblue",
            marker_line_width=2, marker_size=10,
            hovertemplate="Today",
            name="Today",
            # text="Today",
            textfont_size=18,
            textposition="middle right",
        ),
        *(secondary_y, secondary_y) if secondary_y else ()
    )

    fig.add_trace(
        go.Scatter(
            mode="markers", x=[date_eip1559], y=[df.loc[date_eip1559.strftime("%Y-%m-%d")][column][0]],
            marker_symbol=["diamond"],
            # marker_line_color="midnightblue", marker_color="lightskyblue",
            marker_line_width=2, marker_size=10,
            hovertemplate="EIP1559 Enabled",
            name="EIP1559 Enabled",
            # text="EIP1559 Enabled 🔥",
            textfont_size=18,
            textposition="middle right",
        ),
        *(secondary_y, secondary_y) if secondary_y else ()
    )

    fig.add_trace(
        go.Scatter(
            mode="markers", x=[date_pos], y=[df.loc[date_pos.strftime("%Y-%m-%d")][column][0]],
            marker_symbol=["diamond"],
            # marker_line_color="midnightblue", marker_color="lightskyblue",
            marker_line_width=2, marker_size=10,
            hovertemplate="Proof of Stake",
            name="Proof of Stake",
            # text="Proof of Stake 🔱",
            textfont_size=18,
            textposition="middle right",
        ),
        *(secondary_y, secondary_y) if secondary_y else ()
    )

    return fig


def plot_eth_supply_over_all_stages(df):
    df = df.set_index('timestamp', drop=False)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(x=df.timestamp, y=df.eth_supply, name='ETH Supply'),
    )

    fig_add_stage_markers(df, 'eth_supply', fig)
    fig_add_stage_vrects(df, fig)

    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )

    update_legend_names(fig)

    fig.update_layout(
        title="ETH Supply Over Time",
        xaxis_title="Date",
        yaxis_title="ETH Supply (ETH)",
        legend_title="",
    )

    return fig


def plot_eth_supply_and_inflation_over_all_stages(df):
    df = df.set_index('timestamp', drop=False)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=df.timestamp, y=df.eth_supply, name='ETH Supply'),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df.timestamp, y=df.supply_inflation_pct, name='Network Inflation Rate'),
        secondary_y=True,
    )

    fig_add_stage_markers(df, 'eth_supply', fig, secondary_y=False)
    fig_add_stage_vrects(df, fig)

    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )

    update_legend_names(fig)

    fig.update_layout(
        title="ETH Supply and Network Inflation Over Time",
        xaxis_title="Date",
        # yaxis_title="ETH Supply (ETH)",
        legend_title="",
    )

    # Set secondary y-axes titles
    fig.update_yaxes(title_text="ETH Supply (ETH)", secondary_y=False)
    fig.update_yaxes(title_text="Network Inflation Rate (%/year)", secondary_y=True)

    return fig


def plot_network_inflation_over_all_stages(df):
    df = df.set_index('timestamp', drop=False)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(x=df.timestamp, y=df.supply_inflation_pct)  # , fill='tozeroy'
    )

    fig.add_hline(y=0,
                  annotation_text="Ultra-sound barrier",
                  annotation_position="bottom right")

    fig_add_stage_markers(df, 'supply_inflation_pct', fig)
    fig_add_stage_vrects(df, fig)

    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )

    update_legend_names(fig)

    fig.update_layout(
        title="Network Inflation Over Time",
        xaxis_title="Date",
        yaxis_title="Network Inflation Rate (%/year)",
        legend_title="",
    )

    return fig


def plot_eth_staked_over_all_stages(df):
    df = df.set_index('timestamp', drop=False)

    fig = df.plot(x='timestamp', y='eth_staked')

    fig_add_stage_markers(df, 'eth_staked', fig)

    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )

    update_legend_names(fig)

    fig.update_layout(
        title="ETH Staked",
        xaxis_title="Date",
        yaxis_title="ETH Staked (ETH)",
        legend_title="",
    )

    return fig


def plot_number_of_validators_over_time_foreach_subset(df):
    fig = df.plot(x='timestamp', y='number_of_validators', color='subset')

    fig.update_layout(
        title="Number of Validators Over Time",
        xaxis_title="Date",
        yaxis_title="Number of Validators",
    )

    return fig


'''
Experiment 2: Analysis 1
'''

def plot_number_of_validators_in_activation_queue_over_time(df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig_df = df.query('subset == 2')

    fig.add_trace(
        go.Scatter(
            x=fig_df['timestamp'], y=fig_df['number_of_validators'],
            name='Number of validators'
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=fig_df['timestamp'], y=fig_df['number_of_validators_in_activation_queue'],
            name='Activation queue'
        ),
        secondary_y=True
    )

    fig.update_layout(
        title="Number of Validators in Activation Queue Over Time",
        xaxis_title="Date",
    )

    fig.update_yaxes(title_text="Number of Validators", secondary_y=False)
    fig.update_yaxes(title_text="Activation Queue", secondary_y=True)

    update_legend_names(fig)

    return fig


def plot_revenue_profit_yields_over_time_foreach_subset(df):
    fig = df.plot(
        x='timestamp', y=['total_revenue_yields_pct', 'total_profit_yields_pct'],
        facet_col='subset',
        facet_col_wrap=3,
    )

    fig.update_layout(
        title="Revenue and Profit Yields Over Time",
        yaxis_title="Revenue Yield (%/year)",
        hovermode="x"
    )

    fig.for_each_xaxis(lambda x: x.update(dict(title=dict(text='Date'))))

    update_legend_names(fig)

    return fig


def plot_figure_widget_revenue_yields_over_time_foreach_subset(df):
    subset = widgets.Dropdown(
        options=list(df['subset'].unique()),
        value=0,
        description='Scenario:',
    )

    fig_df = df.query('subset == 0')

    trace1 = go.Scatter(
        x=fig_df['timestamp'], y=fig_df['total_revenue_yields_pct'],
    )

    fig = go.FigureWidget(data=[trace1])

    fig.update_layout(
        title="Revenue Yields Over Time",
        xaxis_title="Date",
        yaxis_title="Revenue Yield (%/year)",
        yaxis=dict(
            tickmode='linear',
            dtick=0.5
        )
    )

    max_y = fig_df['total_revenue_yields_pct'].max()
    min_y = fig_df['total_revenue_yields_pct'].min()
    fig.add_hline(y=max_y, line_dash="dot",
                  annotation_text=f"Default scenario max={max_y:.2f}%/year",
                  annotation_position="bottom right")
    fig.add_hline(y=min_y, line_dash="dot",
                  annotation_text=f"Default scenario min={min_y:.2f}%/year",
                  annotation_position="bottom right")

    def response(change):
        _subset = subset.value
        fig_df = df.query(f'subset == {_subset}')

        with fig.batch_update():
            fig.data[0].x = fig_df['timestamp']
            fig.data[0].y = fig_df['total_revenue_yields_pct']

    subset.observe(response, names="value")

    container = widgets.HBox([subset])

    update_legend_names(fig)

    return widgets.VBox([container,
                  fig])


def plot_revenue_yields_rolling_mean(df_rolling):
    fig = go.Figure([
        go.Scatter(
            name='Mean',
            x=df_rolling['timestamp'],
            y=df_rolling['rolling_mean'],
            mode='lines',
            line=dict(color='rgb(31, 119, 180)'),
        ),
        go.Scatter(
            name='Upper Bound (max)',
            x=df_rolling['timestamp'],
            y=df_rolling['max'],
            mode='lines',
            marker=dict(color="#444"),
            line=dict(width=0),
            showlegend=False
        ),
        go.Scatter(
            name='Lower Bound (min)',
            x=df_rolling['timestamp'],
            y=df_rolling['min'],
            marker=dict(color="#444"),
            line=dict(width=0),
            mode='lines',
            fillcolor='rgba(68, 68, 68, 0.3)',
            fill='tonexty',
            showlegend=False
        )
    ])
    fig.update_layout(
        yaxis_title='Revenue Yield (%/year)',
        xaxis_title='Date',
        title='Revenue Yields Rolling Mean Over Time',
        hovermode="x"
    )

    update_legend_names(fig)

    return fig


'''
Experiment 2: Analysis 5
'''

def plot_profit_yields_by_environment_over_time(df):
    validator_profit_yields = [validator.type + '_profit_yields_pct' for validator in validator_environments]

    fig = df.plot(x='timestamp', y=validator_profit_yields)

    fig.update_layout(
        title="Profit Yields by Environment Over Time",
        xaxis_title="Date",
        yaxis_title="Profit Yield (%/year)",
        xaxis=dict(
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )

    update_legend_names(fig)

    return fig
