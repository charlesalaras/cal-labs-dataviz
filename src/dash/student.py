import dash
import flask
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
# db.py
import sys
sys.path.append('../src')
from src.db import get_db, close_db

colors = {
   'background': '#FFFFFF',
   'text': '#12121F'
}

def requestmodules():
   # FIXME: Grab Existing Modules from Database
   conn = get_db()
   modules = conn.execute('SELECT * FROM modules').fetchall()
   close_db()
   options = []
   for module in modules:
      currDict = {
         'label': 'Module ' + str(module[2]),
         'value': module[1]
      }
      options.append(currDict)
   # END OF DATABASE REQUEST
   return options

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
        options=requestmodules(),
        value="Week 2 Module 8: Method of Sections",
        placeholder = "Select a Module"
    ),  
    html.Div(id='dd-output-container', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    html.Div(id='container'),
    html.Div(
        dcc.Graph( id='empty', figure={'data': []}), 
            style={'display': 'none'}
            )
])