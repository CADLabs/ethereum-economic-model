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
import experiments.templates.eth_supply_analysis as eth_supply_analysis
from experiments.run import run
from data.historical_values import df_ether_supply


# Fetch the ETH Supply Analysis experiment
experiment = eth_supply_analysis.experiment
# Create a copy of the experiment simulation
simulation = copy.deepcopy(experiment.simulations[0])
# Default Values
default_pos_launch_date = '2022/09/15'
default_basefee = 30
default_validator_adoption = 3
default_basefee_dropdown_str = f'Enabled (Base Fee = {default_basefee})'
default_validator_adoption_dropdown_str = 'Normal Adoption'
# Configure scenarios
eip1559_scenarios = {'Disabled (Base Fee = 0)': 0, default_basefee_dropdown_str: default_basefee}
validator_scenarios = {
    default_validator_adoption_dropdown_str: default_validator_adoption,
    'Low Adoption': default_validator_adoption * 0.5,
    'High Adoption': default_validator_adoption * 1.5
}


# Load Data
external_stylesheets = ['assets/default_stylesheet.css']

# Build App
app = JupyterDash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    # Inputs
    html.Div([
        # Validator Adoption
        html.Div([
            # Validator Adoption Dropdown
            html.Div([
                html.Label('Validator Adoption Scenario'),
                dcc.Dropdown(
                    id='validator-dropdown',
                    clearable=False,
                    value=default_validator_adoption_dropdown_str,
                    options=[
                        {'label': default_validator_adoption_dropdown_str, 'value': default_validator_adoption_dropdown_str},
                        {'label': 'Low Adoption', 'value': 'Low Adoption'},
                        {'label': 'High Adoption', 'value': 'High Adoption'},
                        {'label': 'Custom Value', 'value': 'Custom Value'}
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
                    value=default_validator_adoption,
                    tooltip={'placement': 'top'}
                )
            ], className='slider-input')
        ], className='input-section'),
        # Proof of Stake Activation Date Dropdown
        html.Div([
            html.Label('Proof-of-Stake Activation Date (\"The Merge\")'),
            dcc.Dropdown(
                id='pos-launch-date-dropdown',
                clearable=False,
                value=default_pos_launch_date,
                options=[
                    {'label': 'Dec 2021', 'value': '2021/12/1'},
                    {'label': 'Mar 2022', 'value': '2022/03/1'},
                    {'label': 'Jun 2022', 'value': '2022/06/1'},
                    {'label': 'Sep 2022', 'value': '2022/09/1'},                  
                    {'label': 'Dec 2022', 'value': '2022/12/1'},
                    {'label': 'Mar 2023', 'value': '2023/03/1'},
                    {'label': 'Jun 2023', 'value': '2023/06/1'}
                ]
            )
        ], className='input-section'),
        # EIP-1559
        html.Div([
            # EIP-1559 Scenarios Dropdown
            html.Div([
                html.Label('EIP1559 Scenario'),
                dcc.Dropdown(
                    id='eip1559-dropdown',
                    clearable=False,
                    value=default_basefee_dropdown_str,
                    options=[
                        {'label': 'Disabled (Base Fee = 0)', 'value': 'Disabled (Base Fee = 0)'},
                        {'label': default_basefee_dropdown_str, 'value': default_basefee_dropdown_str},
                        {'label': 'Enabled (Custom Value)', 'value': 'Enabled (Custom Value)'}
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
                    value=default_basefee,
                    tooltip={'placement': 'top'},
                )
            ], className='slider-input')
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
    if eip1559_dropdown == 'Enabled (Custom Value)':
        raise PreventUpdate

    return eip1559_scenarios[eip1559_dropdown]


@app.callback(
    Output('validator-adoption-slider', 'value'),
    [Input('validator-dropdown', 'value')]
)
def update_validator_adoption_sliders_by_scenarios(validator_dropdown):
    if validator_dropdown == 'Custom Value':
        raise PreventUpdate

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

    _validator_scenarios = dict((v, k) for k, v in validator_scenarios.items())
    validator_dropdown = _validator_scenarios.get(validator_adoption, 'Custom Value')

    _eip1559_scenarios = dict((v, k) for k, v in eip1559_scenarios.items())
    eip1559_dropdown = _eip1559_scenarios.get(eip1559_base_fee, 'Enabled (Custom Value)')

    return (
        validator_dropdown,
        eip1559_dropdown,
        visualizations.plot_eth_supply_and_inflation(df_ether_supply, df, parameters=parameters)
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


def run_eth_supply_simulator(execution_mode=None):
    '''
    Run app and display result in the notebook:
    
    To display in new browser tab at http://127.0.0.1:8050/:
    `run_eth_supply_simulator(execution_mode='external')`

    To display either in "inline" mode when using Jupyter Notebook,
    or "jupyterlab" mode when using Jupyter Lab:
    `run_eth_supply_simulator()`
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
