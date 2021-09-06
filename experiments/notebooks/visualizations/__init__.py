import itertools
import math
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from ipywidgets import widgets
from plotly.subplots import make_subplots

from experiments.notebooks.visualizations.plotly_theme import (
    cadlabs_colors,
    cadlabs_colorway_sequence,
)
from model.system_parameters import parameters, validator_environments
import model.constants as constants


# Set plotly as the default plotting backend for pandas
pd.options.plotting.backend = "plotly"

validator_environment_name_mapping = {
    "custom": "Custom",
    "diy_hardware": "DIY Hardware",
    "diy_cloud": "DIY Cloud",
    "pool_staas": "Pool StaaS",
    "pool_hardware": "Pool Hardware",
    "pool_cloud": "Pool Cloud",
    "staas_full": "StaaS Full",
    "staas_self_custodied": "StaaS Self-custodied",
}

legend_state_variable_name_mapping = {
    "timestamp": "Date",
    "eth_price": "ETH Price",
    "eth_staked": "ETH Staked",
    "eth_supply": "ETH Supply",
    "source_reward_eth": "Source Reward",
    "target_reward_eth": "Target Reward",
    "head_reward_eth": "Head Reward",
    "block_proposer_reward_eth": "Block Proposer Reward",
    "sync_reward_eth": "Sync Reward",
    "total_priority_fee_to_validators_eth": "Priority Fees",
    "total_realized_mev_to_validators": "Realized MEV",
    "supply_inflation_pct": "ETH Supply inflation",
    "total_revenue_yields_pct": "Total Revenue Yields",
    "total_profit_yields_pct": "Total Profit Yields",
    "revenue_profit_yield_spread_pct": "Revenue/Profit Yield Spread",
    **dict(
        [
            (
                validator.type + "_profit_yields_pct",
                validator_environment_name_mapping[validator.type],
            )
            for validator in validator_environments
        ]
    ),
}

axis_state_variable_name_mapping = {
    **legend_state_variable_name_mapping,
    "eth_price": "ETH Price (USD/ETH)",
    "eth_staked": "ETH Staked (ETH)",
    "eth_supply": "ETH Supply (ETH)",
}

millnames = ["", " k", " m", " bn", " tn"]


def millify(n):
    n = float(n)
    millidx = max(
        0,
        min(
            len(millnames) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))
        ),
    )

    return "{:.0f}{}".format(n / 10 ** (3 * millidx), millnames[millidx])


def update_legend_names(fig, name_mapping=legend_state_variable_name_mapping):
    for i, dat in enumerate(fig.data):
        for elem in dat:
            if elem == "name":
                try:
                    fig.data[i].name = name_mapping[fig.data[i].name]
                except KeyError:
                    continue
    return fig


def update_axis_names(fig, name_mapping=axis_state_variable_name_mapping):
    def update_axis_name(axis):
        title = axis["title"]
        text = title["text"]
        updated_text = name_mapping.get(text, text)
        title.update({"text": updated_text})

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
        {
            **axis_state_variable_name_mapping,
            **axis_state_variable_name_mapping_override,
        },
    )
    update_legend_names(
        fig,
        {
            **legend_state_variable_name_mapping,
            **legend_state_variable_name_mapping_override,
        },
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


def plot_validating_rewards(df, subplot_titles=[]):
    validating_rewards = [
        "source_reward_eth",
        "target_reward_eth",
        "head_reward_eth",
        "block_proposer_reward_eth",
        "sync_reward_eth",
    ]

    fig = make_subplots(
        rows=1,
        cols=len(df.subset.unique()),
        shared_yaxes=True,
        subplot_titles=subplot_titles,
    )

    for subset in df.subset.unique():
        color_cycle = itertools.cycle(cadlabs_colorway_sequence)
        df_subset = df.query(f"subset == {subset}")
        for reward_index, reward_key in enumerate(validating_rewards):
            color = next(color_cycle)
            fig.add_trace(
                go.Scatter(
                    x=df_subset.timestamp,
                    y=df_subset[reward_key],
                    stackgroup="one",
                    showlegend=(True if subset == 0 else False),
                    line=dict(color=color),
                    name=validating_rewards[reward_index],
                ),
                row=1,
                col=subset + 1,
            )

    update_legend_names(fig)

    fig.update_layout(
        title="Validating Rewards",
        xaxis_title="Date",
        yaxis_title="Reward (ETH)",
        legend_title="",
    )

    return fig


def plot_validator_incentives_pie_chart(df):
    title = "Validator Incentives (Rewards, Priority Fees, & MEV)"
    validator_rewards = df.iloc[-1][
        [
            "total_priority_fee_to_validators_eth",
            "total_realized_mev_to_validators",
            "source_reward_eth",
            "target_reward_eth",
            "head_reward_eth",
            "block_proposer_reward_eth",
            "sync_reward_eth",
        ]
    ].to_dict()
    labels = [
        "Priority Fees",
        "MEV",
        "Source Reward",
        "Target Reward",
        "Head Reward",
        "Block Proposer Reward",
        "Sync Reward",
    ]

    fig = go.Figure(data=[go.Pie(labels=labels, values=list(validator_rewards.values()), pull=[0.2, 0.2, 0, 0, 0, 0, 0])])

    fig.for_each_trace(
        lambda trace: trace.update(
            textinfo="label+percent",
            insidetextorientation="radial",
            marker=dict(line=dict(color="#000000", width=2)),
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
        go.Scatter(
            x=df_subset_0.eth_staked,
            y=df_subset_0.total_revenue_yields_pct,
            name="Revenue Yields",
            line=dict(color=cadlabs_colorway_sequence[3]),
        ),
    )

    fig.add_trace(
        go.Scatter(
            x=df_subset_0.eth_staked,
            y=df_subset_0.total_profit_yields_pct,
            name=f"Profit Yields @ {df_subset_0.eth_price.iloc[0]:.0f} USD/ETH",
            line=dict(color=cadlabs_colorway_sequence[4], dash="dash"),
        ),
    )

    fig.add_trace(
        go.Scatter(
            x=df_subset_1.eth_staked,
            y=df_subset_1.total_profit_yields_pct,
            name=f"Profit Yields @ {df_subset_1.eth_price.iloc[0]:.0f} USD/ETH",
            line=dict(color=cadlabs_colorway_sequence[5], dash="dash"),
        ),
    )

    update_legend_names(fig)

    fig.update_layout(
        title="Revenue and Profit Yields Over ETH Staked",
        xaxis_title="ETH Staked (ETH)",
        # yaxis_title="",
        legend_title="",
    )

    # Set secondary y-axes titles
    fig.update_yaxes(title_text="Yields (%/year)")
    fig.update_layout(hovermode="x unified")

    return fig


def plot_revenue_profit_yields_over_eth_price(df):
    fig = go.Figure()

    # Add traces
    fig.add_trace(
        go.Scatter(
            x=df.eth_price,
            y=df.total_revenue_yields_pct,
            name=f"Revenue Yields @ ({millify(df.eth_staked.iloc[0])} ETH Staked)",
            line=dict(color=cadlabs_colorway_sequence[3]),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.eth_price,
            y=df.total_profit_yields_pct,
            name=f"Profit Yields @ ({millify(df.eth_staked.iloc[0])} ETH Staked)",
            line=dict(color=cadlabs_colorway_sequence[4], dash="dash"),
        ),
    )

    update_legend_names(fig)

    fig.update_layout(
        title="Revenue and Profit Yields Over ETH Price",
        xaxis_title="ETH Price (USD/ETH)",
        # yaxis_title="",
        legend_title="",
    )

    # Set secondary y-axes titles
    fig.update_yaxes(title_text="Yields (%/year)")
    fig.update_layout(hovermode="x unified")

    return fig


def plot_validator_environment_yields(df):
    validator_profit_yields_pct = [
        validator.type + "_profit_yields_pct" for validator in validator_environments
    ]

    fig = df.plot(
        x="eth_price",
        y=(validator_profit_yields_pct + ["total_profit_yields_pct"]),
        facet_col="subset",
        facet_col_wrap=2,
        facet_col_spacing=0.05,
    )

    fig.for_each_annotation(
        lambda a: a.update(
            text=f"ETH Staked = {df.query(f'subset == {a.text.split(chr(61))[1]}').eth_staked.iloc[0]:.0f} ETH"
        )
    )

    fig.update_layout(
        title=f"Profit Yields of Validator Environments",
        xaxis_title="ETH Price (USD/ETH)",
        yaxis_title="Profit Yields (%/year)",
        legend_title="",
    )

    fig.for_each_xaxis(lambda x: x["title"].update({"text": "ETH Price (USD/ETH)"}))
    fig.update_yaxes(matches=None)
    fig.update_yaxes(showticklabels=True)

    update_legend_names(fig)

    return fig


def plot_three_region_yield_analysis(fig_df):
    fig = fig_df.plot(
        x="eth_price",
        y=["total_revenue_yields_pct", "total_profit_yields_pct"],
    )

    fig.add_annotation(
        x=fig_df["eth_price"].min() + 100,
        y=fig_df["total_revenue_yields_pct"].max(),
        text="Cliff",
        showarrow=False,
        yshift=10,
    )

    fig.add_annotation(
        x=fig_df["eth_price"].median(),
        y=fig_df["total_revenue_yields_pct"].max(),
        text="Economics of Scale",
        showarrow=False,
        yshift=10,
    )

    fig.add_annotation(
        x=fig_df["eth_price"].max() - 100,
        y=fig_df["total_revenue_yields_pct"].max(),
        text="Stability",
        showarrow=False,
        yshift=10,
    )

    update_legend_names(fig)

    fig.update_layout(
        title=f"Three Region Yield Analysis @ {millify(fig_df.eth_staked.iloc[0])} ETH Staked",
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
        go.Scatter(
            x=df_subset_0.eth_staked,
            y=df_subset_0.total_revenue_yields_pct,
            name="Revenue Yields",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df_subset_0.eth_staked,
            y=df_subset_0.total_profit_yields_pct,
            name=f"Profit Yields @ {df_subset_0.eth_price.iloc[0]} USD/ETH",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df_subset_1.eth_staked,
            y=df_subset_1.total_profit_yields_pct,
            name=f"Profit Yields @ {df_subset_1.eth_price.iloc[0]} USD/ETH",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df_subset_0.eth_staked,
            y=df_subset_0.supply_inflation_pct,
            name="Network Inflation Rate",
        ),
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

    fig = go.Figure(
        data=[
            go.Contour(
                x=x,
                y=y,
                z=z,
                line_smoothing=0.85,
                colorscale=cadlabs_colors,
                colorbar=dict(
                    title="Profit Yields (%/year)",
                    titleside="right",
                    titlefont=dict(size=14),
                ),
            )
        ]
    )

    update_legend_names(fig)

    fig.update_layout(
        title="Profit Yields Over ETH Price vs. ETH Staked",
        xaxis_title="ETH Price (USD/ETH)",
        yaxis_title="ETH Staked (ETH)",
        width=1000,
        legend_title="",
        autosize=False,
    )

    return fig


def plot_revenue_profit_yield_spread(df):
    grouped = df.groupby(["eth_price", "eth_staked"]).last()[
        "revenue_profit_yield_spread_pct"
    ]

    x = df.groupby(["run"]).first()["eth_price"].unique()
    y = df.groupby(["run"]).first()["eth_staked"].unique()
    z = []

    for eth_staked in y:
        row = []
        for eth_price in x:
            z_value = grouped[eth_price][eth_staked]
            row.append(z_value)
        z.append(row)

    fig = go.Figure(
        data=[
            go.Contour(
                x=x,
                y=y,
                z=z,
                line_smoothing=0.85,
                contours=dict(
                    showlabels=True,  # show labels on contours
                    labelfont=dict(  # label font properties
                        size=12,
                        color="white",
                    ),
                ),
                colorbar=dict(
                    title="Spread (%/year)", titleside="right", titlefont=dict(size=14)
                ),
                colorscale=cadlabs_colors,
            )
        ]
    )

    update_legend_names(fig)

    fig.update_layout(
        title="Revenue/Profit Yield Spread Over ETH Price vs. ETH Staked",
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

    fig = go.Figure(
        data=[
            go.Surface(
                x=x,
                y=y,
                z=z,
                colorbar=dict(
                    title="Profit Yields (%/year)",
                    titleside="right",
                    titlefont=dict(size=14),
                ),
                colorscale=cadlabs_colors,
            )
        ]
    )

    fig.update_traces(contours_z=dict(show=True, usecolormap=True, project_z=True))

    update_legend_names(fig)

    fig.update_layout(
        title="Profit Yields Over ETH Price vs. ETH Staked",
        autosize=False,
        legend_title="",
        margin=dict(l=65, r=50, b=65, t=90),
        scene={
            "xaxis": {
                "title": {"text": "ETH Price (USD/ETH)"},
                "type": "log",
            },
            "yaxis": {"title": {"text": "ETH Staked (ETH)"}},
            "zaxis": {"title": {"text": "Profit Yields (%/year)"}},
        },
    )

    return fig


def fig_add_stage_vrects(df, fig, parameters=parameters):
    date_start = parameters["date_start"][0]
    date_eip1559 = parameters["date_eip1559"][0]
    date_pos = parameters["date_pos"][0]
    date_end = df.index[-1]

    fig.add_vrect(
        x0=date_eip1559,
        x1=date_pos,
        row="all",
        col=1,
        layer="below",
        fillcolor="gray",
        opacity=0.25,
        line_width=0,
    )

    fig.add_vrect(
        x0=date_pos,
        x1=date_end,
        row="all",
        col=1,
        layer="below",
        fillcolor="gray",
        opacity=0.1,
        line_width=0,
    )
    return fig


def fig_add_stage_markers(df, column, fig, secondary_y=None, parameters=parameters):
    # Frontier 📆 Jul-30-2015 03:26:13 PM +UTC
    # Frontier thawing Sep-07-2015 09:33:09 PM +UTC
    # Homestead Mar-14-2016 06:49:53 PM +UTC
    # DAO fork Jul-20-2016 01:20:40 PM +UTC
    # Tangerine whistle Oct-18-2016 01:19:31 PM +UTC
    # Spurious Dragon Nov-22-2016 04:15:44 PM +UTC
    # Byzantium Oct-16-2017 05:22:11 AM +UTC
    # Constantinople Feb-28-2019 07:52:04 PM +UTC
    # Istanbul Dec-08-2019 12:25:09 AM +UTC
    # Muir Glacier Jan-02-2020 08:30:49 AM +UTC
    # Staking deposit contract deployed Oct-14-2020 09:22:52 AM +UTC
    # Beacon Chain genesis Dec-01-2020 12:00:35 PM +UTC

    historical_dates = [
        ("Frontier", datetime.strptime("Jul-30-2015", "%b-%d-%Y"), (-20, 45)),
        ("Frontier thawing", datetime.strptime("Sep-07-2015", "%b-%d-%Y"), (35, 50)),
        ("Homestead", datetime.strptime("Mar-14-2016", "%b-%d-%Y"), (-30, 0)),
        ("Byzantium", datetime.strptime("Oct-16-2017", "%b-%d-%Y"), (30, 40)),
        ("Constantinople", datetime.strptime("Feb-28-2019", "%b-%d-%Y"), (30, -15)),
        ("Istanbul", datetime.strptime("Dec-08-2019", "%b-%d-%Y"), (30, -10)),
        ("Muir Glacier", datetime.strptime("Jan-02-2020", "%b-%d-%Y"), (-35, 0)),
    ]

    system_dates = [
        ("Beacon Chain", datetime.strptime("Dec-01-2020", "%b-%d-%Y")),
        # ("Today", parameters["date_start"][0]),
        ("EIP1559", parameters["date_eip1559"][0]),
        ("Proof of Stake", parameters["date_pos"][0]),
    ]

    for (name, date, (ay, ax)) in historical_dates:
        nearest_row = df.iloc[
            df.index.get_loc(date.strftime("%Y-%m-%d"), method="nearest")
        ]
        x_datetime = nearest_row["timestamp"][0]
        y_value = nearest_row[column][0]
        fig.add_annotation(
            x=x_datetime,
            y=y_value,
            text=name,
            ay=ay,
            ax=ax,
            showarrow=True,
            arrowhead=2,
            arrowsize=1.25,
        )

    for idx, (name, date) in enumerate(system_dates):
        if date > parameters["date_start"][0]:
            x_datetime = date
            y_value = df.loc[date.strftime("%Y-%m-%d")][column][0]

        else:
            nearest_row = df.iloc[
                df.index.get_loc(date.strftime("%Y-%m-%d"), method="nearest")
            ]
            x_datetime = nearest_row["timestamp"][0]
            y_value = nearest_row[column][0]
                

        fig.add_trace(
            go.Scatter(
                mode="markers+text",
                x=[x_datetime],
                y=[y_value],
                marker_symbol=["diamond"],
                marker_line_width=2,
                marker_size=10,
                hovertemplate=name,
                name=name,
                # textfont_size=11,
                text=name,
                textposition="top center",
                legendgroup="markers",
                showlegend=False,
            ),
            *(secondary_y, secondary_y) if secondary_y else (),
        )

    return fig


def plot_eth_supply_over_all_stages(df):
    df = df.set_index("timestamp", drop=False)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(x=df.timestamp, y=df.eth_supply, name="ETH Supply"),
    )

    fig_add_stage_markers(df, "eth_supply", fig)
    fig_add_stage_vrects(df, fig)

    # Add range slider
    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))

    update_legend_names(fig)

    fig.update_layout(
        title="ETH Supply Over Time",
        xaxis_title="Date",
        yaxis_title="ETH Supply (ETH)",
        legend_title="",
    )

    return fig


def plot_eth_supply_and_inflation(df_historical, df_simulated, parameters=parameters):
    df_historical = df_historical.set_index("timestamp", drop=False)
    df_simulated = df_simulated.set_index("timestamp", drop=False)

    df_historical["supply_inflation_pct"] = df_historical[
        "supply_inflation_pct_rolling"
    ]
    df_historical = df_historical.drop(df_historical.tail(1).index)
    df_historical.loc[df_simulated.index[0]] = df_simulated.iloc[0]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=df_historical.timestamp,
            y=df_historical.supply_inflation_pct,
            name="Historical Network Inflation Rate",
            line=dict(color="#FC1CBF"),
            legendgroup="historical",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df_historical.timestamp,
            y=df_historical.eth_supply,
            name="Historical ETH Supply",
            line=dict(color="#3283FE"),
            legendgroup="historical",
        ),
        secondary_y=True,
    )

    for subset in df_simulated.subset.unique():
        df_subset = df_simulated.query(f"subset == {subset}")
        fig.add_trace(
            go.Scatter(
                x=df_subset.timestamp,
                y=df_subset.supply_inflation_pct,
                name="Simulated Network Inflation Rate",
                line=dict(color="#FC1CBF", dash="dot"),
                showlegend=(True if subset == 0 else False),
                legendgroup="simulated",
            ),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(
                x=df_subset.timestamp,
                y=df_subset.eth_supply,
                name="Simulated ETH Supply",
                line=dict(color="#3283FE", dash="dot"),
                showlegend=(True if subset == 0 else False),
                legendgroup="simulated",
            ),
            secondary_y=True,
        )
        # fill=('tonexty' if subset > 0 else None)

    df = df_historical.append(df_simulated)

    fig_add_stage_markers(
        df, "supply_inflation_pct", fig, secondary_y=False, parameters=parameters
    )
    fig_add_stage_vrects(df, fig, parameters=parameters)

    date_inflation_annotation = datetime.strptime("Dec-01-2024", "%b-%d-%Y")
    fig.add_annotation(
        x=date_inflation_annotation,
        y=-2.75,
        text="Deflationary",
        showarrow=True,
        ay=-35,
        ax=0,
        arrowhead=2,
        arrowsize=1.25,
    )

    fig.add_annotation(
        x=date_inflation_annotation,
        y=2.75,
        text="Inflationary",
        showarrow=True,
        ay=35,
        ax=0,
        arrowhead=2,
        arrowsize=1.25,
    )

    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True,
            ),
            rangeslider_thickness=0.15,
            type="date",
        )
    )

    update_legend_names(fig)

    fig.update_layout(
        xaxis_title="Date",
        title="ETH Supply Simulator",
        legend_title="",
        height=550,
        legend=dict(
            title=dict(
                text="",
            ),
            orientation="h",
            yanchor="top",
            y=-0.475,
            xanchor="center",
            x=0.5,
            traceorder="grouped",
            itemclick=False,
        ),
        margin=dict(l=60, r=0, t=30, b=20),
    )

    fig.add_hline(
        y=0,
        line_color="#808080",
        line_width=0.75,
        annotation_text="",
        annotation_position="bottom right",
    )

    # Set secondary y-axes titles
    fig.update_yaxes(title_text="Network Inflation Rate (%/year)", secondary_y=False)
    fig.update_yaxes(title_text="ETH Supply (ETH)", secondary_y=True)

    return fig


def plot_network_inflation_over_all_stages(df):
    df = df.set_index("timestamp", drop=False)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(x=df.timestamp, y=df.supply_inflation_pct)  # , fill='tozeroy'
    )

    fig.add_hline(
        y=0, annotation_text="Ultra-sound barrier", annotation_position="bottom right"
    )

    fig_add_stage_markers(df, "supply_inflation_pct", fig)
    fig_add_stage_vrects(df, fig)

    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))

    update_legend_names(fig)

    fig.update_layout(
        title="Network Inflation Over Time",
        xaxis_title="Date",
        yaxis_title="Network Inflation Rate (%/year)",
        legend_title="",
    )

    return fig


def plot_eth_staked_over_all_stages(df):
    df = df.set_index("timestamp", drop=False)

    fig = df.plot(x="timestamp", y="eth_staked")

    fig_add_stage_markers(df, "eth_staked", fig)

    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))

    update_legend_names(fig)

    fig.update_layout(
        title="ETH Staked",
        xaxis_title="Date",
        yaxis_title="ETH Staked (ETH)",
        legend_title="",
    )

    return fig


def plot_number_of_validators_per_subset(df, scenario_names):
    fig = go.Figure()

    for subset in df.subset.unique():
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[df.subset == subset]["number_of_active_validators"],
                name=scenario_names[subset],
            )
        )

    fig.update_layout(
        title="Validator Adoption Scenarios",
        xaxis_title="Date",
        yaxis_title="Active Validators",
        legend_title="",
        xaxis=dict(rangeslider=dict(visible=True)),
    )
    fig.update_layout(hovermode="x unified")

    return fig


def plot_number_of_validators_in_activation_queue_over_time(df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig_df = df.query("subset == 2")

    fig.add_trace(
        go.Scatter(
            x=fig_df["timestamp"],
            y=fig_df["number_of_validators"],
            name="Number of validators",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=fig_df["timestamp"],
            y=fig_df["number_of_validators_in_activation_queue"],
            name="Activation queue",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title="Number of Validators in Activation Queue Over Time",
        xaxis_title="Date",
    )

    fig.update_yaxes(title_text="Number of Validators", secondary_y=False)
    fig.update_yaxes(title_text="Activation Queue", secondary_y=True)

    update_legend_names(fig)

    return fig


def plot_yields_per_subset_subplots(df, subplot_titles=[]):
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)

    fig = make_subplots(
        rows=1, cols=3, shared_yaxes=True, subplot_titles=subplot_titles
    )

    for subset in df.subset.unique():
        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[df.subset == subset]["total_revenue_yields_pct"],
                name="Revenue Yields",
                line=dict(color=color),
                showlegend=False,
            ),
            row=1,
            col=subset + 1,
        )
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[df.subset == subset]["total_profit_yields_pct"],
                name="Profit Yields",
                line=dict(color=color, dash="dash"),
                showlegend=False,
            ),
            row=1,
            col=subset + 1,
        )

    # Add uncoloured legend for traces
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=[None],
            mode="lines",
            line=dict(color="black"),
            name="Revenue Yields",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=[None],
            mode="lines",
            line=dict(color="black", dash="dash"),
            name="Profit Yields",
        )
    )

    fig.update_layout(
        title="Revenue and Profit Yields Over Time - At a Glance",
        xaxis_title="Date",
        yaxis_title="Revenue Yields (%/year)",
        legend_title="",
        hovermode="x",
    )

    fig.for_each_xaxis(lambda x: x.update(dict(title=dict(text="Date"))))

    # Removes the 'subset=' from the facet_col title
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    update_legend_names(fig)

    return fig


def plot_yields_per_subset(df, scenario_names):
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)

    fig = go.Figure()

    for subset in df.subset.unique():
        df_subset = df.query(f"subset == {subset}").copy()

        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df_subset["total_revenue_yields_pct"],
                name=f"{scenario_names[subset]} Revenue Yields",
                line=dict(color=color),
            ),
        )
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df_subset["total_profit_yields_pct"],
                name=f"{scenario_names[subset]} Profit Yields",
                line=dict(color=color, dash="dash"),
                visible=False,
            ),
        )

    fig.update_layout(
        title="Revenue or Profit Yields Over Time",
        xaxis_title="Date",
        yaxis_title="Yields (%/year)",
        legend_title="",
    )

    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                buttons=[
                    dict(
                        label="Revenue Yields",
                        method="update",
                        args=[{"visible": [True, "legendonly"]}, {"showlegend": True}],
                    ),
                    dict(
                        label="Profit Yields",
                        method="update",
                        args=[{"visible": ["legendonly", True]}, {"showlegend": True}],
                    ),
                ],
                direction="right",
                showactive=True,
                pad={"t": 10},
                x=0,
                xanchor="left",
                y=1.3,
                yanchor="top",
            )
        ]
    )

    fig.update_layout(hovermode="x unified")

    return fig


def plot_cumulative_yields_per_subset(df, DELTA_TIME, scenario_names):
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)

    fig = go.Figure()

    for subset in df.subset.unique():
        df_subset = df.query(f"subset == {subset}").copy()

        df_subset["daily_revenue_yields_pct"] = (
            df_subset["total_revenue_yields_pct"] / (constants.epochs_per_year / DELTA_TIME)
        )
        df_subset["daily_profit_yields_pct"] = (

            df_subset["total_profit_yields_pct"] / (constants.epochs_per_year / DELTA_TIME)
        )

        df_subset["cumulative_revenue_yields_pct"] = (
            df_subset["daily_revenue_yields_pct"].expanding().sum()
        )
        df_subset["cumulative_profit_yields_pct"] = (
            df_subset["daily_profit_yields_pct"].expanding().sum()
        )

        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df_subset["cumulative_revenue_yields_pct"],
                name=f"{scenario_names[subset]} Revenue Yields",
                line=dict(color=color),
            ),
        )
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df_subset["cumulative_profit_yields_pct"],
                name=f"{scenario_names[subset]} Profit Yields",
                line=dict(color=color, dash="dash"),
                visible=False,
            ),
        )

    fig.update_layout(
        title="Cumulative Revenue or Profit Yields Over Time",
        xaxis_title="Date",
        yaxis_title="Cumulative Yields (%)",
        legend_title="",
    )

    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                buttons=[
                    dict(
                        label="Revenue Yields",
                        method="update",
                        args=[{"visible": [True, "legendonly"]}, {"showlegend": True}],
                    ),
                    dict(
                        label="Profit Yields",
                        method="update",
                        args=[{"visible": ["legendonly", True]}, {"showlegend": True}],
                    ),
                ],
                direction="right",
                showactive=True,
                pad={"t": 10},
                x=0,
                xanchor="left",
                y=1.3,
                yanchor="top",
            )
        ]
    )

    fig.update_layout(hovermode="x unified")

    return fig


def plot_cumulative_revenue_yields_per_subset(df, scenario_names):
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)

    fig = go.Figure()

    for subset in df.subset.unique():
        df_subset = df.query(f"subset == {subset}").copy()

        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df_subset["cumulative_revenue_yields_pct"],
                name=f"{scenario_names[subset]}",
                line=dict(color=color),
            ),
        )

    fig.update_layout(
        title="Cumulative Revenue Yields Over Time",
        xaxis_title="Date",
        yaxis_title="Cumulative Revenue Yields (%)",
        legend_title="",
    )

    fig.update_layout(hovermode="x unified")

    return fig


def plot_stacked_cumulative_column_per_subset(df, column, scenario_names):
    color_cycle = itertools.cycle([
        "#782AB6",
        "#1C8356",
        "#F6222E",
    ])

    fig = go.Figure()

    for subset in df.subset.unique():
        df_subset = df.query(f"subset == {subset}").copy()

        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df_subset[column],
                name=f"{scenario_names[subset]}",
                line=dict(color=color),
                stackgroup='one',
            ),
        )

    fig.update_layout(
        hovermode="x unified",
        margin=dict(r=30, b=65, l=80),
        xaxis_title="Date",
        xaxis=dict(
            rangeslider=dict(
                visible=True,
            ),
            rangeslider_thickness=0.15,
            type="date",
        )
    )

    return fig


def plot_cumulative_returns_per_subset(df):
    scenario_names = {0: "Normal Adoption", 1: "Low Adoption", 2: "High Adoption"}
    color_cycle = itertools.cycle(cadlabs_colorway_sequence)

    fig = go.Figure()

    for subset in df.subset.unique():
        df_subset = df.query(f"subset == {subset}").copy()

        df_subset["daily_revenue_yields_pct"] = (
            df_subset["total_revenue_yields_pct"] / 365
        )
        df_subset["daily_profit_yields_pct"] = (
            df_subset["total_profit_yields_pct"] / 365
        )

        df_subset["cumulative_revenue_yields_pct"] = (
            df_subset["daily_revenue_yields_pct"].expanding().sum()
        )
        df_subset["cumulative_profit_yields_pct"] = (
            df_subset["daily_profit_yields_pct"].expanding().sum()
        )

        df_subset["cumulative_revenue"] = (
            1 + df_subset["cumulative_revenue_yields_pct"] / 100
        )
        df_subset["cumulative_profit"] = (
            1 + df_subset["cumulative_revenue_yields_pct"] / 100
        )

        color = next(color_cycle)
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df_subset["cumulative_revenue"],
                name=f"{scenario_names[subset]} Revenue Yields",
                line=dict(color=color),
            ),
        )
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df_subset["cumulative_profit"],
                name=f"{scenario_names[subset]} Profit Yields",
                line=dict(color=color, dash="dash"),
                visible=False,
            ),
        )

    fig.update_layout(
        title="Cumulative Revenue or Profit Returns Over Time",
        xaxis_title="Date",
        yaxis_title="Cumulative Returns (USD)",
        legend_title="",
    )

    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                buttons=[
                    dict(
                        label="Revenue Yields",
                        method="update",
                        args=[{"visible": [True, "legendonly"]}, {"showlegend": True}],
                    ),
                    dict(
                        label="Profit Yields",
                        method="update",
                        args=[{"visible": ["legendonly", True]}, {"showlegend": True}],
                    ),
                ],
                direction="right",
                showactive=True,
                pad={"t": 10},
                x=0,
                xanchor="left",
                y=1.1,
                yanchor="top",
            )
        ]
    )

    fig.update_layout(hovermode="x unified")

    return fig


def plot_figure_widget_revenue_yields_over_time_foreach_subset(df):
    subset = widgets.Dropdown(
        options=list(df["subset"].unique()),
        value=0,
        description="Scenario:",
    )

    fig_df = df.query("subset == 0")

    trace1 = go.Scatter(
        x=fig_df["timestamp"],
        y=fig_df["total_revenue_yields_pct"],
    )

    fig = go.FigureWidget(data=[trace1])

    fig.update_layout(
        title="Revenue Yields Over Time",
        xaxis_title="Date",
        yaxis_title="Revenue Yields (%/year)",
        yaxis=dict(tickmode="linear", dtick=0.5),
    )

    max_y = fig_df["total_revenue_yields_pct"].max()
    min_y = fig_df["total_revenue_yields_pct"].min()
    fig.add_hline(
        y=max_y,
        line_dash="dot",
        annotation_text=f"Default scenario max={max_y:.2f}%/year",
        annotation_position="bottom right",
    )
    fig.add_hline(
        y=min_y,
        line_dash="dot",
        annotation_text=f"Default scenario min={min_y:.2f}%/year",
        annotation_position="bottom right",
    )

    def response(change):
        _subset = subset.value
        fig_df = df.query(f"subset == {_subset}")

        with fig.batch_update():
            fig.data[0].x = fig_df["timestamp"]
            fig.data[0].y = fig_df["total_revenue_yields_pct"]

    subset.observe(response, names="value")

    container = widgets.HBox([subset])

    update_legend_names(fig)

    return widgets.VBox([container, fig])


def plot_revenue_yields_rolling_mean(df):
    
    rolling_window = df.groupby('timestamp')['total_revenue_yields_pct'].mean().rolling(7)
    df_rolling = pd.DataFrame()
    df_rolling['rolling_std'] = rolling_window.std()
    df_rolling['rolling_mean'] = rolling_window.mean()
    df_rolling['max'] = df.groupby('timestamp')['total_revenue_yields_pct'].max()
    df_rolling['min'] = df.groupby('timestamp')['total_revenue_yields_pct'].min()
    df_rolling = df_rolling.fillna(method="ffill")
    df_rolling = df_rolling.reset_index()
    
    fig = go.Figure(
        [
            go.Scatter(
                name="Mean",
                x=df_rolling["timestamp"],
                y=df_rolling["rolling_mean"],
                mode="lines",
            ),
            go.Scatter(
                name="Max",
                x=df_rolling["timestamp"],
                y=df_rolling["max"],
                mode="lines",
                marker=dict(color="#444"),
                line=dict(width=0),
                showlegend=False,
            ),
            go.Scatter(
                name="Min",
                x=df_rolling["timestamp"],
                y=df_rolling["min"],
                marker=dict(color="#444"),
                line=dict(width=0),
                mode="lines",
                fillcolor="rgba(68, 68, 68, 0.3)",
                fill="tonexty",
                showlegend=False,
            ),
        ]
    )
    fig.update_layout(
        yaxis_title="Revenue Yields (%/year)",
        xaxis_title="Date",
        title="Revenue Yields Rolling Mean Over Time",
        hovermode="x",
    )

    update_legend_names(fig)

    return fig


def plot_profit_yields_by_environment_over_time(df):
    validator_profit_yields = [
        validator.type + "_profit_yields_pct" for validator in validator_environments
    ]

    fig = go.Figure()

    for key in validator_profit_yields:
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[key],
                name=legend_state_variable_name_mapping[key],
            )
        )

    fig.update_layout(
        title="Profit Yields by Environment Over Time",
        xaxis_title="Date",
        yaxis_title="Profit Yields (%/year)",
        legend_title="",
        xaxis=dict(rangeslider=dict(visible=True), type="date"),
        hovermode="x unified",
    )

    return fig


def plot_network_issuance_scenarios(df, simulation_names):
    df = df.set_index("timestamp", drop=False)

    fig = go.Figure()

    initial_simulation = 0
    for subset in df.query(f"simulation == {initial_simulation}").subset.unique():
        simulation_key = list(simulation_names.keys())[initial_simulation]
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df.query(
                    f"subset == {subset} and simulation == {initial_simulation}"
                ).eth_supply,
                name=simulation_names[simulation_key][subset],
                visible=True,
            )
        )

    buttons = []

    for simulation_index in df.simulation.unique():
        simulation_key = list(simulation_names.keys())[simulation_index]
        simulation_df = df.query(f"simulation == {simulation_index}")
        subset_len = len(simulation_df.subset.unique())
        visible_traces = [False for i in range(4)]
        visible_traces[:subset_len] = [True for i in range(subset_len)]
        buttons.append(
            dict(
                method="update",
                label=str(simulation_key),
                visible=True,
                args=[
                    {
                        "visible": visible_traces,
                        "y": [
                            simulation_df.query(f"subset == {subset}").eth_supply
                            for subset in simulation_df.subset.unique()
                        ],
                        "x": [df.index],
                        "name": list(
                            [
                                simulation_names[simulation_key][subset]
                                for subset in simulation_df.subset.unique()
                            ]
                        ),
                        "type": "scatter",
                    }
                ],
            )
        )

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                buttons=buttons,
                direction="right",
                showactive=True,
                pad={"t": 25},
                x=0,
                xanchor="left",
                y=1.25,
                yanchor="top",
            )
        ]
    )

    fig.update_layout(
        yaxis_title="ETH Supply (ETH)",
        xaxis_title="Date",
        title="Inflation Rate and ETH Supply Analysis Scenarios",
        hovermode="x unified",
    )

    return fig
