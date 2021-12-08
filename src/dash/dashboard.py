# Layout pulled from https://github.com/guptaraghav29/PythonPlotly

import dash
import flask
from dash import dcc
from dash import html
from .instructor import instructor_layout
from .student import student_layout
from dash.dependencies import Input, Output
import json

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
      if pathname == '/dashapp/instructor':
         return instructor_layout
      elif pathname == '/dashapp/student':
         return student_layout
      else:
         return '404'