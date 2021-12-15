import dash
import flask
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from .data import fig_objects
# Might not work, need to ensure
from .db import get_db

colors = {
   'background': '#FFFFFF',
   'text': '#12121F'
}

fig = fig_objects[0]

fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

# Layout for Instructor View
instructor_layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Demo for hosted web app',
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
        style={'margin': 'auto'}
        # FIXME: Grab Existing Modules from Database
        """
        conn = get_db()
        modules = conn.execute('SELECT * FROM modules').fetchall()
        close_db()
        options = []
        for module in modules:
            currDict = {
                'label': 'Module ' + module[1],
                'value': 'Module ' + module[1] + ': ' + module[2]
            }
            options.append(currDict)
            value = module[2] # Is value necessary?...
        """
        # END OF DATABASE REQUEST
        options= [{'label': 'Module 1' , 'value' : 'Name of graph one'} , {'label': 'Module 2' , 'value' : 'Name of graph two'} ],
        value = 'Name of graph one'
        multi =True
        placeholder="Select a Module"
    ),  
    html.Div(id='dd-output-container', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
     dcc.Graph(
        id='example-graph-2',
        figure=fig
    ),
    html.Div(id='container'),
    html.Div(
        dcc.Graph( id='empty', figure={'data': []}), 
            style={'display': 'none'}
            )
])
