import plotly.graph_objects as go
import plotly.io as pio
import sys


default_template = go.layout.Template()

default_template.layout.height = 800  # pixels

default_template.layout.title = dict(
    x=0.5
)
default_template.layout.xaxis = dict(
    showgrid=True
)
default_template.layout.yaxis = dict(
    showgrid=True
)

# Legend at bottom of chart
# default_template.layout.legend = dict(
#     title=dict(
#         text="",
#     ),
#     orientation="h",
#     yanchor="bottom",
#     y=-0.2,
#     xanchor="center",
#     x=0.5,
# )

pio.templates["default"] = default_template
# Other options: "presentation", "simple_white"
pio.templates.default = "plotly_white+default"
