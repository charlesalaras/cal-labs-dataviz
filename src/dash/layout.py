import dash
from dash import dcc
from dash import html

import sys
sys.path.append('../src')
from src.db import get_db, close_db, db_connect, db_close

colors = {
    'background': '#FFFFFF',
    'text': '#000020'
}

def request_modules():
    db = db_connect()
    modules = db.callabs.modules.find({"active": True})
    options = []
    for module in modules:
        currDict = {
            'label': module["name"],
            'value': module["_id"]
        }
        options.append(currDict)
    db_close(db)
    # END OF DATABASE REQUEST
    return options
def request_topics():
    topics = []
    options = []
    for topic in topics:
        currDict = {
            'label': topic["name"],
            'value': topic["_id"]
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
