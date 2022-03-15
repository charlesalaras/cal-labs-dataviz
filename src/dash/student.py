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
   modules = conn.execute('SELECT name, id FROM modules').fetchall()
   close_db()
   options = []
   for module in modules:
      currDict = {
         'label': module[0],
         'value': module[1]
      }
      options.append(currDict)
   # END OF DATABASE REQUEST
   return options

# Layout for Student View
student_layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Cal Labs Data Analysis',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='Welcome, {email}', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Dropdown(
        className='twelve columns',
        id='student-figure',
        options=requestmodules(),
        value="Week 2 Module 8: Method of Sections"
    ),
    dcc.Input(
        className='twelve columns',
        id='student-email',
        type='email',
        placeholder='Enter Email Here',
        value=""
    ),
    html.Div(id='dd-output-container', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    html.Div(id='student-container'),
    html.Div(
        dcc.Graph( id='empty', figure={'data': []}),
            style={'display': 'none'}
            )
])
