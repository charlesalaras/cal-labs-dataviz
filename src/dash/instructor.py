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

# Layout for Instructor View
instructor_layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Cal Labs Class Analysis',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='Instructor View', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Dropdown(
        className='four columns',
        id='figure-list',
        style={'margin': 'auto', 'display': 'block'},
        options=requestmodules(),
        value='Week 2 Module 8: Method of Sections'
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
