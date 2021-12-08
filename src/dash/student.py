import dash
import flask
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

# Layout for Student View
student_layout = html.Div([
    html.H3('Student'),
    dcc.Dropdown(
        id='student-dropdown',
        options=[
            {'label': 'App 2 - {}'.format(i), 'value': i} for i in [
                'NYC', 'MTL', 'LA'
            ]
        ]
    )
])