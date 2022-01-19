import dash
import flask
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from .question import create_questions
from .instructor import requestmodules

colors = {
    'background': '#111111',
    'text': '#FFFFFF'
}

question_layout = html.Div(
    style ={'backgroundColor': colors['background']},
    children=[
        html.H1(
            children='Module Overview',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),
        dcc.Dropdown(
            className='twelve columns',
            id='module-list',
            style={
                'margin': 'auto',
                'display': 'block',
                'background-color': '#222222',
                'color': 'white'
            },
            options=requestmodules(),
            value='Moment'
        ),
        html.Div(
            id='dd-output-container',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),
        html.Div(
            id='questions-container'
        )
    ]
)
