import plotly.graph_objects as go
import plotly.io as pio


cadlabs_colors = [
    [0, "#1AD5A0"],
    [0.33, "#30B4F1"],
    [0.66, "#D03DD2"],
    [1.0, "#F76746"],
]
cadlabs_colors_r = [
    [0, "#F76746"],
    [0.33, "#D03DD2"],
    [0.66, "#30B4F1"],
    [1.0, "#1AD5A0"],
]
cadlabs_colorway_sequence = [
    "#FC1CBF",
    "#3283FE",
    "#1CBE4F",
    "#AA0DFE",
    "#FA0087",
    "#FE00FA",
    "#1C8356",
    "#782AB6",
    "#F6222E",
    "#B10DA1",
]


layout_width = 1200
layout_height = 675


pio.templates["cadlabs"] = go.layout.Template(
    layout_font={"color": "#2a3f5f"},
    layout_plot_bgcolor="white",
    layout_paper_bgcolor="white",
    # layout_width=layout_width,
    # layout_height=layout_height,
    layout_colorway=cadlabs_colorway_sequence,
    layout_xaxis={
        "automargin": True,
        "showgrid": True,
        "gridcolor": "#EBF0F8",
        "linecolor": "#EBF0F8",
        "ticks": "",
        "title": {"standoff": 15},
        "zerolinecolor": "#EBF0F8",
        "zerolinewidth": 2,
        "rangeslider": {
            "bordercolor": "#E0E0E0",
            "borderwidth": 2,
            "bgcolor": "#FCFCFC",
            "thickness": 0.18,
        },
    },
    layout_yaxis={
        "automargin": True,
        "showgrid": True,
        "gridcolor": "#EBF0F8",
        "linecolor": "#EBF0F8",
        "ticks": "",
        "title": {"standoff": 15},
        "zerolinecolor": "#EBF0F8",
        "zerolinewidth": 2,
    },
    layout_scene={
        "xaxis": {
            "backgroundcolor": "white",
            "gridcolor": "#DFE8F3",
            "gridwidth": 2,
            "linecolor": "#EBF0F8",
            "showbackground": True,
            "ticks": "",
            "zerolinecolor": "#EBF0F8",
        },
        "yaxis": {
            "backgroundcolor": "white",
            "gridcolor": "#DFE8F3",
            "gridwidth": 2,
            "linecolor": "#EBF0F8",
            "showbackground": True,
            "ticks": "",
            "zerolinecolor": "#EBF0F8",
        },
        "zaxis": {
            "backgroundcolor": "white",
            "gridcolor": "#DFE8F3",
            "gridwidth": 2,
            "linecolor": "#EBF0F8",
            "showbackground": True,
            "ticks": "",
            "zerolinecolor": "#EBF0F8",
        },
    },
    layout_shapedefaults={"line": {"color": "#2a3f5f"}},
    layout_ternary={
        "aaxis": {"gridcolor": "#DFE8F3", "linecolor": "#A2B1C6", "ticks": ""},
        "baxis": {"gridcolor": "#DFE8F3", "linecolor": "#A2B1C6", "ticks": ""},
        "bgcolor": "white",
        "caxis": {"gridcolor": "#DFE8F3", "linecolor": "#A2B1C6", "ticks": ""},
    },
    layout_annotationdefaults={
        "arrowcolor": "#2a3f5f",
        "arrowhead": 0,
        "arrowwidth": 1,
    },
    layout_autotypenumbers="strict",
    layout_coloraxis={"colorbar": {"outlinewidth": 0, "ticks": ""}},
    layout_colorscale={"sequential": cadlabs_colors},
    layout_hoverlabel={"align": "left"},
    layout_hovermode="closest",
    layout_mapbox={"style": "light"},
    layout_geo={
        "bgcolor": "white",
        "lakecolor": "white",
        "landcolor": "white",
        "showlakes": True,
        "showland": True,
        "subunitcolor": "#C8D4E3",
    },
    layout_polar={
        "angularaxis": {"gridcolor": "#EBF0F8", "linecolor": "#EBF0F8", "ticks": ""},
        "bgcolor": "white",
        "radialaxis": {"gridcolor": "#EBF0F8", "linecolor": "#EBF0F8", "ticks": ""},
    },
)


pio.templates["cadlabs_dark"] = go.layout.Template(
    layout_font={"color": "#f2f5fa"},
    layout_plot_bgcolor="rgb(17,17,17)",
    layout_paper_bgcolor="rgb(17,17,17)",
    # layout_width=layout_width,
    # layout_height=layout_height,
    layout_colorway=cadlabs_colorway_sequence,
    layout_xaxis={
        "automargin": True,
        "showgrid": True,
        "gridcolor": "#283442",
        "linecolor": "#506784",
        "ticks": "",
        "title": {"standoff": 15},
        "zerolinecolor": "#283442",
        "zerolinewidth": 2,
        "rangeslider": {
            "bordercolor": "#3A3A3A",
            "borderwidth": 2,
            "bgcolor": "rgb(17,17,17)",
            "thickness": 0.18,
        },
    },
    layout_yaxis={
        "automargin": True,
        "showgrid": True,
        "gridcolor": "#283442",
        "linecolor": "#506784",
        "ticks": "",
        "title": {"standoff": 15},
        "zerolinecolor": "#283442",
        "zerolinewidth": 2,
    },
    layout_colorscale={"sequential": cadlabs_colors},
)


pio.templates["cadlabs_frontend"] = go.layout.Template(
    # layout_width=layout_width,
    # layout_height=layout_height,
    layout_font={"color": "#ffffff"},
    layout_plot_bgcolor="#272838",
    layout_paper_bgcolor="#272838",
    layout_colorway=cadlabs_colorway_sequence,
    layout_xaxis={
        "automargin": True,
        "showgrid": True,
        "gridcolor": "#3C3D56",
        "linecolor": "#3C3D56",
        "ticks": "",
        "title": {"standoff": 15},
        "zerolinecolor": "#272838",
        "zerolinewidth": 3,
        "rangeslider": {
            "bordercolor": "#3C3D56",
            "borderwidth": 2,
            "bgcolor": "#272838",
            "thickness": 0.18,
        },
    },
    layout_yaxis={
        "automargin": True,
        "showgrid": True,
        "gridcolor": "#3C3D56",
        "linecolor": "#3C3D56",
        "ticks": "",
        "title": {"standoff": 15},
        "zerolinecolor": "#3C3D56",
        "zerolinewidth": 3,
    },
    layout_colorscale={"sequential": cadlabs_colors}
)


# Set this to one of the custom themes above to change default
pio.templates.default = "cadlabs"

# Legend at bottom of chart
# pio.templates["cadlabs"].layout.legend = dict(
#     title=dict(
#         text="",
#     ),
#     orientation="h",
#     yanchor="bottom",
#     y=-0.7,
#     xanchor="center",
#     x=0.5,
# )
