import dash
import flask
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

# Layout for Instructor View
instructor_layout = html.Div([
    html.H3('Instructor'),
    dcc.Dropdown(
        id='app-1-dropdown',
        options=[
            {'label': 'App 1 - {}'.format(i), 'value': i} for i in [
                'NYC', 'MTL', 'LA'
            ]
        ]
    )
])