import plotly.express as px
from datetime import date
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import copy
from datetime import datetime

import experiments.notebooks.visualizations as visualizations
import experiments.notebooks.visualizations.plotly_theme
import experiments.templates.time_domain_analysis as time_domain_analysis
from experiments.run import run
from data.historical_values import df_ether_supply


# Fetch the time-domain analysis experiment
experiment = time_domain_analysis.experiment
# Create a copy of the experiment simulation
simulation = copy.deepcopy(experiment.simulations[0])

# Load Data
external_stylesheets = ['assets/default_stylesheet.css']

# Build App
app = JupyterDash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    # Inputs
    html.Div([
        html.H1('Peak ETH Simulator'),
        # Validator Adoption
        html.Div([
            # Validator Adoption Dropdown
            html.Div([
                html.Label("Validator Adoption Scenario"),
                dcc.Dropdown(
                id='validator-dropdown',
                clearable=False,
                value=3,
                options=[
                    {'label': 'Normal Adoption', 'value': 3},
                    {'label': 'Low Adoption', 'value': 3 * 0.5},
                    {'label': 'High Adoption', 'value': 3 * 1.5},
                    {'label': 'Custom', 'value': 'Custom'}
                ] 
                )
            ]), 
            # Validator Adoption Slider
            html.Div([
                html.Label("New Validators per Epoch"),
                dcc.Slider(
                    id='validator-adoption-slider',
                    min=0,
                    max=10,
                    step=0.5,
                    marks={
                        0: '0',
                        5: '5',
                        10: '10',
                    },
                    value=3,
                    tooltip={'placement': 'top'}
                )
            ])
            
        ], className='validator-section'),
        # Proof of Stake Activation Date Dropdown
        html.Div([
            html.Label("Proof-of-Stake Activation Date (\"The Merge\")"),
            dcc.Dropdown(
                id='pos-launch-date-dropdown',
                clearable=False,
                value='2021/12/1',
                options=[
                    {'label': 'Dec 2021', 'value': '2021/12/1'},
                    {'label': 'Mar 2022', 'value': '2022/03/1'},
                    {'label': 'Jun 2022', 'value': '2022/06/1'},
                    {'label': 'Sep 2022', 'value': '2022/09/1'}
                ]
            )
        ], className='pos-date-section'),
        # EIP1559
        html.Div([
            # EIP1559 Scenarios Dropdown
            html.Div([
                html.Label("EIP1559 Scenarios"),
                dcc.Dropdown(
                    id='eip1559-dropdown',
                    clearable=False,
                    value='Enabled: Steady State',
                    options=[
                        {'label': 'Disabled', 'value': 'Disabled'},
                        {'label': 'Enabled: Steady State', 'value': 'Enabled: Steady State'},
                        {'label': 'Enabled: MEV', 'value': 'Enabled: MEV'},
                        {'label': 'Custom', 'value': 'Custom'}
                    ]
                )
            ]),
            # Basefee slider
            html.Div([
                html.Label("Basefee (Gwei per gas)"),
                dcc.Slider(
                    id='eip1559-basefee-slider',
                    min=0,
                    max=100,
                    step=1,
                    marks={
                        0: '0',
                        25: '25',
                        50: '50',
                        75: '75',
                        100: '100'
                    },
                    value=100,
                    tooltip={'placement': 'top'},
                )
            ]),
            # Validator Tips Slider
            html.Div([
                html.Label("Average Priority Fee (Gwei per gas)"),
                dcc.Slider(
                    id='eip1559-validator-tips-slider',
                    min=0,
                    max=100,
                    step=1,
                    marks={
                        0: '0',
                        25: '25',
                        50: '50',
                        75: '75',
                        100: '100'
                    },
                    value=1,
                    tooltip={'placement': 'top'}
                )
            ])
        ], className='eip1559-section')
    ], className='input-row'),
    
    # Output
    html.Div([
        dcc.Loading(
            id='loading-1',
            children=[dcc.Graph(id='graph', style={'height': '700px'})],
            type='default'
        )
    ], className='output-row')
])

# Callbacks
@app.callback(
    Output('eip1559-basefee-slider', 'value'),
    Output('eip1559-validator-tips-slider', 'value'),
    [Input('eip1559-dropdown', 'value')]
)
def update_eip1559_sliders_by_scenarios(eip1559_dropdown):
    eip1559_scenarios = {'Disabled': [0, 0], 'Enabled: Steady State': [100, 1], 'Enabled: MEV': [70, 30]}
    if eip1559_dropdown == 'Custom':
        raise PreventUpdate
    return eip1559_scenarios[eip1559_dropdown][0], eip1559_scenarios[eip1559_dropdown][1]


@app.callback(
    Output('validator-adoption-slider', 'value'),
    [Input('validator-dropdown', 'value')]
)
def update_validator_adoption_sliders_by_scenarios(validator_dropdown):
    return validator_dropdown


def run_simulation(validators_per_epoch, pos_launch_date, eip1559_basefee, eip1559_avg_tip):
    simulation.model.params.update({
        'validator_process': [
            lambda _run, _timestep: float(validators_per_epoch),
        ],
        'date_pos': [
            datetime.strptime(pos_launch_date, "%Y/%m/%d")
        ],
        'eip1559_basefee_process': [
            lambda _run, _timestep: float(eip1559_basefee), 
        ],  # Gwei per gas
        'eip1559_tip_process': [
            lambda _run, _timestep: float(eip1559_avg_tip),
        ],  # Gwei per gas
    })

    df, _exceptions = run(simulation)
    
    return df, simulation.model.params


# Define callback to update graph
@app.callback(
    Output('validator-dropdown', 'value'),
    Output('eip1559-dropdown', 'value'),
    Output('graph', 'figure'),
    [Input("validator-adoption-slider", "value"),
     Input("pos-launch-date-dropdown", "value"),
     Input("eip1559-basefee-slider", "value"),
     Input("eip1559-validator-tips-slider", "value")]
)
def update_output_graph(validator_adoption, pos_launch_date, eip1559_basefee, eip1559_validator_tips):
    df, parameters = run_simulation(validator_adoption, pos_launch_date, eip1559_basefee, eip1559_validator_tips)
    
    if validator_adoption not in [1.5, 3, 4.5]:
        validator_adoption = 'Custom'

    eip1559_fees = [eip1559_basefee, eip1559_validator_tips]
    if eip1559_fees in [[0, 0], [100, 1], [70, 30]]:
        if eip1559_fees == [0, 0]:
            eip1559 = 'Disabled'
        elif eip1559_fees == [100, 1]:
            eip1559 = 'Enabled: Steady State'
        else:
            eip1559 = 'Enabled: MEV'
    else:
        eip1559 = 'Custom'

    return (
        validator_adoption,
        eip1559,
        visualizations.plot_eth_supply_and_inflation_over_all_stages(df_ether_supply, df, parameters=parameters)
    )


def run_peak_eth_simulator():
    # Run app and display result inline in the notebook
    app.run_server(mode='inline')
