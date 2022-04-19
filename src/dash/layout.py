import dash
from dash import dcc
from dash import html

import sys
sys.path.append('../src')
from src.db import get_db, close_db

colors = {
    'background': '#FFFFFF',
    'text': '#000020'
}

def request_modules():
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
def request_topics():
    conn = get_db()
    topics = conn.execute('SELECT id, title FROM topics').fetchall()
    close_db()
    options = []
    for topic in topics:
        currDict = {
            'label': topic[1],
            'value': topic[0]
        }
        options.append(currDict)
    # END OF DATABASE REQUEST
    return options

def create_layout():
    return (
        html.Div(
            id='page',
            children=[
                dcc.Location(id='url', refresh=True),
                html.Div(
                    className='logout',
                    children=html.A(href="/logout", children="Logout")
                ),
                html.H1(
                    children='California Learning Lab Data Analysis',
                    style={ 'textAlign': 'center' }
                ),
                html.Div(
                    id='auth-user-info',
                    style={ 'textAlign': 'center' }
                ),
                dcc.Tabs(
                    className='twelve columns',
                    value='by-module',
                    id='tabs',
                    children=[
                        dcc.Tab(label='MODULE OVERVIEW',
                            value='by-module',
                            children=[
                                dcc.Dropdown(
                                    className='twelve columns',
                                    id='module-list',
                                    placeholder='Select a Module',
                                    options=request_modules()
                                    ),
                                dcc.Loading(
                                    className="twelve columns",
                                    id="module-loading",
                                    type="circle",
                                    children=html.Div(id='module-content', className='twelve columns'))
                                ]
                        ),
                        dcc.Tab(label='TOPIC OVERVIEW',
                            value='by-topic',
                            children=[
                                dcc.Dropdown(
                                    className='twelve columns',
                                    id='topic-list',
                                    placeholder='Select Topics Here',
                                    multi=True,
                                    options=request_topics()
                                    ),
                                dcc.Loading(
                                    className="twelve columns",
                                    id="topic-loading",
                                    type="circle",
                                    children=html.Div(id='topics-content', className='twelve columns'))
                                ]
                        )
                ]),
            ]
        )
    )
