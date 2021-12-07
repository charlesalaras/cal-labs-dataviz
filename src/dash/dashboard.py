# Layout pulled from https://github.com/guptaraghav29/PythonPlotly

import dash
from dash import dcc
from dash import html
import json
import plotly.express as px
import pandas as pd
from pandas import json_normalize
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from .data import fig_objects

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]

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

def init_dashboard(server):
   dash_app = dash.Dash(
      server=server,
      routes_pathname_prefix='/dashapp/',
      external_stylesheets=external_stylesheets
   )

   # Create Dash Layout
   dash_app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
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

   init_callbacks(dash_app)

   return dash_app.server

def init_callbacks(app):
   @app.callback(
   Output('dd-output-container', 'children'), 
      Input('figure-list', 'value')
   )

   def update_output(value):
      return 'You have selected "{}"'.format(value)

   @app.callback(Output('example-graph-2', 'figure'),
      Input('figure-list', 'value'))

   def update_figure_output(value):
      if value == 'Name of graph two':
         figure = fig_objects[1]
      else : figure = fig_objects[0] 
      return figure

   @app.callback(Output('container', 'children'),
      Input('figure-list', 'value'))
   def addinggraphsfromlist(value):
      if value == 'Name of graph two':
         graphs = []
         for i in range(0,len(fig_objects)):
            graphs.append(dcc.Graph(
               className='six columns',
               id='graph-{}'.format(i),
               figure= fig_objects[i]
            ))
      return html.Div(graphs)