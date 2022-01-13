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


# JavaScript External MathJAX
external_scripts=[
   "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML"
]

def init_dashboard(server):
   dash_app = dash.Dash(
      server=server,
      routes_pathname_prefix='/dashapp/',
      external_scripts=external_scripts
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
         columnSpacing = 'six columns'
         if i == 0:
             columnSpacing = 'twelve columns'
         # Add Relevant Question
         if i % 3 == 1 and j < len(questions):
            graphs.append(html.Div(
                className=(columnSpacing + ' fig'),
                id='question-{}'.format(j),
                children=questions[j]
            ))
            j = j + 1
         # Add Relevant Graph
         graphs.append(dcc.Graph(
            className=(columnSpacing + ' fig'),
            id='graph-{}'.format(i),
            figure= fig_objects[i]
         ))
      return html.Div(graphs)
