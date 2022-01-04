# Layout pulled from https://github.com/guptaraghav29/PythonPlotly

import dash
import flask
from dash import dcc
from dash import html
from .instructor import instructor_layout
from .student import student_layout
from dash.dependencies import Input, Output
import json
from .data import create_data
from .question import create_questions

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
         return html.H1(
            children='404: Page Not Found',
            style={
            'textAlign': 'center'
         })
   @app.callback(
   Output('dd-output-container', 'children'),
      Input('figure-list', 'value')
   )
   def update_output(value):
      return html.H4(
         children='You have selected "{}"'.format(value),
         style={
         'textAlign': 'center'
         })

   @app.callback(Output('container', 'children'),
      Input('figure-list', 'value'))
   def addinggraphsfromlist(value):
      fig_objects = create_data(value)
      questions = create_questions(value)
      graphs = []
      j = 0
      for i in range(0,len(fig_objects)):
         # Add Relevant Question
         if i % 3 == 1 and j < len(questions):
            graphs.append(html.Div(
                className='five columns',
                id='question-{}'.format(j),
                children=questions[j]
            ))
            j = j + 1
         # Add Relevant Graph
         graphs.append(dcc.Graph(
            className='five columns',
            id='graph-{}'.format(i),
            figure= fig_objects[i]
         ))
      return html.Div(graphs)
