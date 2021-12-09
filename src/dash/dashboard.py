# Layout pulled from https://github.com/guptaraghav29/PythonPlotly

import dash
import flask
from dash import dcc
from dash import html
from .instructor import instructor_layout
from .student import student_layout
from dash.dependencies import Input, Output
import json
from .data import fig_objects

# CSS External Stylesheet
external_stylesheets = [
   'https://codepen.io/chriddyp/pen/bWLwgP.css',
   {
      'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
      'rel': 'stylesheet',
      'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
      'crossorigin': 'anonymous'
   }
]

def init_dashboard(server):
   dash_app = dash.Dash(
      server=server,
      routes_pathname_prefix='/dashapp/',
      external_stylesheets=external_stylesheets
   )

   dash_app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

   init_callbacks(dash_app)

   return dash_app.server

def init_callbacks(app):
   @app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
   def display_page(pathname):
      # and tokenized id is instructor
      if pathname == '/dashapp/instructor':
         return instructor_layout
      # and tokenized id is student
      elif pathname == '/dashapp/student':
         return student_layout
      else:
         return '404'
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
               className='five columns',
               id='graph-{}'.format(i),
               figure= fig_objects[i]
            ))
      return html.Div(graphs)