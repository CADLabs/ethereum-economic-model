import plotly.express as px
from datetime import date
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import copy
from datetime import datetime
import psutil

import experiments.notebooks.visualizations as visualizations
import experiments.notebooks.visualizations.plotly_theme
import experiments.templates.time_domain_analysis as time_domain_analysis
from experiments.run import run
from data.historical_values import df_ether_supply


# Do some pre-processing on historic data
df_ether_supply['supply_inflation_pct'] = df_ether_supply['supply_inflation_pct'].rolling(14).mean()

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
                html.Label('Validator Adoption Scenario'),
                dcc.Dropdown(
                    id='validator-dropdown',
                    clearable=False,
                    value='Normal Adoption',
                    options=[
                        {'label': 'Normal Adoption', 'value': 'Normal Adoption'},
                        {'label': 'Low Adoption', 'value': 'Low Adoption'},
                        {'label': 'High Adoption', 'value': 'High Adoption'},
                        {'label': 'Custom', 'value': 'Custom'}
                    ]
                )
            ]),
            # Validator Adoption Slider
            html.Div([
                html.Label('New Validators per Epoch'),
                dcc.Slider(
                    id='validator-adoption-slider',
                    min=0,
                    max=7.5,
                    step=0.5,
                    marks={
                        0: '0',
                        4: '4',
                        7.5: '7.5',
                    },
                    value=3,
                    tooltip={'placement': 'top'}
                )
            ])
        ], className='input-section'),
        # Proof of Stake Activation Date Dropdown
        html.Div([
            html.Label('Proof-of-Stake Activation Date (\"The Merge\")'),
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
        ], className='input-section'),
        # EIP1559
        html.Div([
            # EIP1559 Scenarios Dropdown
            html.Div([
                html.Label('EIP1559 Scenarios'),
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
            # Base fee slider
            html.Div([
                html.Label('Base Fee (Gwei per gas)'),
                dcc.Slider(
                    id='eip1559-base-fee-slider',
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
            ])
        ], className='input-section')
    ], className='input-row'),

    # Output
    html.Div([
        dcc.Loading(
            id='loading-1',
            children=[dcc.Graph(id='graph')],
            type='default'
        )
    ], className='output-row')
])


# Callbacks
@app.callback(
    Output('eip1559-base-fee-slider', 'value'),
    [Input('eip1559-dropdown', 'value')]
)
def update_eip1559_sliders_by_scenarios(eip1559_dropdown):
    if eip1559_dropdown == 'Custom':
        raise PreventUpdate

    eip1559_scenarios = {'Disabled': 0, 'Enabled: Steady State': 100, 'Enabled: MEV': 70}

    return eip1559_scenarios[eip1559_dropdown]


@app.callback(
    Output('validator-adoption-slider', 'value'),
    [Input('validator-dropdown', 'value')]
)
def update_validator_adoption_sliders_by_scenarios(validator_dropdown):
    if validator_dropdown == 'Custom':
        raise PreventUpdate

    validator_scenarios = {'Normal Adoption': 3, 'Low Adoption': 3 * 0.5, 'High Adoption': 3 * 1.5}

    return validator_scenarios[validator_dropdown]


# Define callback to update graph
@app.callback(
    Output('validator-dropdown', 'value'),
    Output('eip1559-dropdown', 'value'),
    Output('graph', 'figure'),
    [Input('validator-adoption-slider', 'value'),
     Input('pos-launch-date-dropdown', 'value'),
     Input('eip1559-base-fee-slider', 'value')]
)
def update_output_graph(validator_adoption, pos_launch_date, eip1559_base_fee):
    df, parameters = run_simulation(validator_adoption, pos_launch_date, eip1559_base_fee)

    if validator_adoption == 3:
        validator_dropdown = 'Normal Adoption'
    elif validator_adoption == 3 * 0.5:
        validator_dropdown = 'Low Adoption'
    elif validator_adoption == 3 * 1.5:
        validator_dropdown = 'High Adoption'
    else:
        validator_dropdown = 'Custom'

    if eip1559_base_fee == 0:
        eip1559_dropdown = 'Disabled'
    elif eip1559_base_fee == 100:
        eip1559_dropdown = 'Enabled: Steady State'
    elif eip1559_base_fee == 70:
        eip1559_dropdown = 'Enabled: MEV'
    else:
        eip1559_dropdown = 'Custom'

    return (
        validator_dropdown,
        eip1559_dropdown,
        visualizations.plot_eth_supply_and_inflation_over_all_stages(df_ether_supply, df, parameters=parameters)
    )


def run_simulation(validators_per_epoch, pos_launch_date, eip1559_base_fee):
    simulation.model.params.update({
        'validator_process': [
            lambda _run, _timestep: float(validators_per_epoch),
        ],
        'date_pos': [
            datetime.strptime(pos_launch_date, '%Y/%m/%d')
        ],
        'base_fee_process': [
            lambda _run, _timestep: float(eip1559_base_fee),
        ],  # Gwei per gas
    })

    df, _exceptions = run(simulation)

    return df, simulation.model.params


def run_peak_eth_simulator(execution_mode=None):
    '''
    Run app and display result in the notebook:
    
    To display in new browser tab at http://127.0.0.1:8050/:
    `run_peak_eth_simulator(execution_mode='external')`

    To display either in "inline" mode when using Jupyter Notebook,
    or "jupyterlab" mode when using Jupyter Lab:
    `run_peak_eth_simulator()`
    '''
    processes = psutil.Process().parent().cmdline()
    is_jupyter_lab = any('lab' in p for p in processes)
    if execution_mode:
        pass
    elif is_jupyter_lab:
        execution_mode = 'jupyterlab'
    else:
        execution_mode = 'inline'
    app.run_server(mode=execution_mode, height=1200, debug=False)
