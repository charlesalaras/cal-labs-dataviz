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
from .admin import ADMINS

from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

# JavaScript External MathJAX
external_scripts=[
   "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML"
]

def init_dashboard(server):
   dash_app = dash.Dash(
      server=server,
      url_base_pathname='/dashapp/',
      external_scripts=external_scripts
   )

   dash_app.layout = create_layout

   init_callbacks(dash_app)

   return dash_app.server

def init_callbacks(app):
   @app.callback(Output('url', 'pathname'),
                 Input('url', 'pathname'))
   def auth_dashboard(pathname):
       if pathname == '/dashapp/' and not current_user.is_authenticated:
          return '/'
       else:
          return '/dashapp/'
   @app.callback(Output('auth-user-info', 'children'),
                 Input('url', 'pathname'))
   def render_info(pathname):
       if pathname == '/dashapp/' and current_user.is_authenticated:
           content = [html.Img(src=str(current_user.profile_pic)), html.H3(str(current_user.name)), html.P(str(current_user.email))]
           if str(current_user.email) in ADMINS:
               content.append(html.Div(className="admin", children="Instructor"))
           else:
               content.append(html.Div(className="student", children="Student"))
           return content
       else: # How did you get here?!
           return "NOT LOGGED IN"
   @app.callback(Output('topics-content', 'children'),
                 Input('topic-list', 'value'))
   def topics_content(topics):
       return html.P("Current topics: " + str(topics))
   @app.callback(Output('module-content', 'children'),
                 Input('module-list', 'value'))
   def module_content(module):
       if module == None:
           return html.Div("No module selected!")
       if current_user.is_authenticated:
           questions = create_questions(module)
           # IF Instructor Mode: DO THIS
           if str(current_user.email) in ADMINS:
               lrs = parse_lrs(module)
               fig_objects = create_questionGraphs(lrs, module)
               content = [html.Div(className='twelve columns', children=topicAnalysis(lrs, module))]

               averages = createAverages(lrs, module)
               content.append(html.Div(className='twelve columns', children=dcc.Tabs(className='twelve columns', children=[
                   dcc.Tab(label='Average Time', children=averages[0]),
                   dcc.Tab(label='Average Score per Question', children=averages[1]),
                   dcc.Tab(label='Average Overall Score', children=averages[2])])))

               content.append(html.Div(className='twelve columns', children=unique_actors(lrs, module)))
           # ELSE: Student Mode DO THIS
           else:
               lrs = parse_lrs(module, "mailto:" + str(current_user.email))
               fig_objects = create_questionGraphs(lrs, module, "mailto:" + str(current_user.email))
               content = [html.Div(className='twelve columns', children=topicAnalysis(lrs, module, "mailto:" + str(current_user.email)))]

           j = 0 # Question Counter Variable
           for i in fig_objects.keys():
              q_id = findQuestion(i, module) # Find the question needed

              content.append(html.Div(className='twelve columns', children=dcc.Tabs(children=[
                  dcc.Tab(label='Question', children=questions[str(q_id)]),
                  dcc.Tab(label='Responses', children=fig_objects[i][0]),
                  dcc.Tab(label='Score Statistics', children=fig_objects[i][1]),
                  dcc.Tab(label='Average Statistics', children=fig_objects[i][2])])))
              j = j + 1
       else:
           return html.Div("ERROR: Access denied.")
       return content
