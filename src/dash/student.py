import dash
import flask
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from .data import fig_objects

colors = {
   'background': '#FFFFFF',
   'text': '#12121F'
}

fig = fig_objects[0]

fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

# Layout for Student View
student_layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Demo for hosted web app',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='Dash: A web application framework for Python.', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Dropdown(
        className='four columns',
        id='figure-list',
        options= [{'label': 'Module 1' , 'value' : 'Name of graph one'} , {'label': 'Module 2' , 'value' : 'Name of graph two'} ],
        value = 'Name of graph one'
    ),  
    html.Div(id='dd-output-container', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
     dcc.Graph(
        id='example-graph-2',
        figure=fig
    ),
    html.Div(id='container'),
    html.Div(
        dcc.Graph( id='empty', figure={'data': []}), 
            style={'display': 'none'}
            )
])