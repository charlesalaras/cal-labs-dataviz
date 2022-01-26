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
   'background': '#111111',
   'text': '#FFFFFF'
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
        id='figure-list',
        options=requestmodules(),
        value="Moment"
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
    html.Div(id='container'),
    html.Div(
        dcc.Graph( id='empty', figure={'data': []}),
            style={'display': 'none'}
            )
])
