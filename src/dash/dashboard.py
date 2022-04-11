# Layout pulled from https://github.com/guptaraghav29/PythonPlotly

import dash
import flask
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import json
from .data import create_data
from .question import create_questions
from .layout import create_layout
from .new_data import *
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

   dash_app.layout = create_layout

   init_callbacks(dash_app)

   return dash_app.server

def init_callbacks(app):
   @app.callback(Output('topics-content', 'children'),
                 Input('topic-list', 'value'))
   def topics_content(topics):
       return html.P("Current topics: " + str(topics))
   @app.callback(Output('module-content', 'children'),
                 Input('module-list', 'value'))
   def module_content(module):
       if module == None:
           return html.Div("No module selected!")
       questions = create_questions(module)
       lrs = parse_lrs(module)
       # IF Instructor Mode: DO THIS
       fig_objects = create_questionGraphs(lrs, module)
       content = [html.Div(className='twelve columns', children=topicAnalysis(lrs, module))]

       averages = createAverages(lrs, module)
       content.append(html.Div(className='twelve columns', children=dcc.Tabs(className='twelve columns', children=[
           dcc.Tab(label='Average Time', children=averages[0]),
           dcc.Tab(label='Average Score per Question', children=averages[1]),
           dcc.Tab(label='Average Overall Score', children=averages[2])
           ])))

       content.append(html.Div(className='twelve columns', children=unique_actors(lrs, module)))
       # ELSE: Student Mode DO THIS
       """
       fig_objects = create_questionGraphs(lrs, module, actor)
       content = [html.Div(className='twelve columns', children=topicAnalysis(lrs, module, actor)))]
       """
       j = 0 # Question Counter Variable
       for i in fig_objects.keys():
          q_id = findQuestion(i, module) # Find the question needed

          content.append(html.Div(className='twelve columns', children=dcc.Tabs(children=[
              dcc.Tab(label='Question', children=questions[str(q_id)]),
              dcc.Tab(label='Responses', children=fig_objects[i][0]),
              dcc.Tab(label='Score Statistics', children=fig_objects[i][1]),
              dcc.Tab(label='Average Statistics', children=fig_objects[i][2])
                      ])))
          j = j + 1
       return content
