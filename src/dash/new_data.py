import json
import sys
import math
import pandas as pd
from dash import dcc
import plotly as plotly
import plotly.express as px
import plotly.graph_objects as go
from pandas import json_normalize
from types import SimpleNamespace
sys.path.append('../src')
from src.db import get_db, close_db
from src.dash.topics import topics as def_topics

def checkCorrect(student_answers, desc) {
   # Find question that matches descriptor
   # Find answer key that matches question
   # Compare lists (true / false)
      # Compare List Size
      # Compare Answer Slugs
   return True
}
def parse_lrs(module, actor="any"): # Parses out the LRS
   # Open and Parse LRS JSON
   with open('ucrstaticsw22.json') as json_file:
      xapiData = json.load(json_file)

   lrs = json_normalize(xapiData)

   # Stores Course Link
   del lrs['object.id']
   # Stores 'Activity'
   del lrs['object.objectType']
   # Stores type link
   del lrs['object.definition.type']
   # Stores Access Level
   del lrs['authority.objectType']
   # Stores LRS Link
   del lrs['authority.account.homePage']
   # Stores 'authorization'
   del lrs['authority.account.name']
   # Stores verb link
   del lrs['verb.id']
   # Stores timestamp loaded
   del lrs['stored']
   # Stores User Email
   # del lrs['actor.mbox']
   # Stores Minimum Possible Score (If Available)
   del lrs['result.score.min']
   conn = get_db()
   module = conn.execute('SELECT name FROM modules WHERE id=:module', {'module': module}).fetchone()
   close_db()
   temp = lrs.loc[lrs['object.definition.name.en-US'] == str(module[0])].copy()
   # FIXME: If Actor is Instructor, Skip this Step
   if actor != "any":
      temp = temp.loc[temp['actor.mbox'] == actor].copy()

   # ISO8601 Parser (Maybe a Library that Does this?)
   for x in temp.index:
       # Parse Hours
       if 'H' in temp.at[x, 'result.duration']:
           time_string = temp.at [x, 'result.duration']
           temp.at[x, 'result.duration'] = pd.to_datetime(temp.at[x, 'result.duration'], format='PT%HH%MM%SS').time()
       # Parse Minutes
       elif 'M' in temp.at[x, 'result.duration']:
           time_string = temp.at [x, 'result.duration']
           temp.at[x, 'result.duration'] = pd.to_datetime(temp.at[x, 'result.duration'], format='PT%MM%SS').time()
       # Parse Seconds
       else:
           time_string = temp.at [x, 'result.duration']
           temp.at[x, 'result.duration'] = pd.to_datetime(temp.at[x, 'result.duration'], format='PT%SS').time()
   lrs = temp.copy()

   # %%
   # create time delta from datetime.time objects
   lrs['result.duration.seconds'] = 'NaN'

   temp = lrs.copy()
   for x in temp.index:
       time_string = temp.at [x, 'result.duration']
       temp.at[x, 'result.duration.seconds'] = pd.to_timedelta(time_string.strftime( format="%H:%M:%S")).total_seconds()
   lrs = temp.copy()

   return lrs

def unique_actors(lrs, module): # For Instructor Only: Get Unique Actors for Module
   # Note, we passed in ID, might wanna get actual name from DB...
   # conn = get_db()
   # module = conn.execute('SELECT name FROM modules WHERE id=:module', {'module': module}).fetchone()
   # close_db()

   fig = go.Figure()

   fig.add_trace(go.Indicator(
       mode = 'number',
       value = lrs['actor.name'].nunique(),
       title = {'text': "unique actors"},
        domain = {'row': 0, 'column': 0}
       ))

   temp = lrs.loc[lrs['verb.display.en-US'] == "exited"].copy()

   fig.add_trace(go.Indicator(
       mode = 'number',
       number = {'suffix': ' mins'},
       value = (temp['result.duration.seconds'].mean() / 60) ,
       title = {'text': "Average Module Completion"},
       domain = {'row': 0, 'column': 1}
       ))
   # create grid
   fig.update_layout(
       grid = {'rows': 2, 'columns': 2})
   return dcc.Graph(figure=fig)

def response_table(lrs):
   data = lrs.sort_values(by=['result.extensions.http://id.tincanapi.com/extension/attempt-id'])
   fig = go.Figure(data=[go.Table(
      header=dict(values=['Attempt Number', 'Response', 'Duration'], align='center'),
      cells=dict(values=[temp['result.extensions.http://id.tincanapi.com/extension/attempt-id'], temp['result.response'], temp['result.duration.seconds']], align='center'))
   ])
   return fig

def create_questionGraphs(lrs, module, actor="any"): # Create Question Figures
   # Filter into "answered" statements + Create an Index
   temp = lrs.loc[(lrs['verb.display.en-US'] == "answered") ].copy()
   temp_desc = temp['object.definition.description.en-US'].unique()

   figures = {}
   for x in range(0, temp_desc.size):
      currSet = []
      question_data = temp.loc[(temp['object.definition.description.en-US'] == temp_desc[x])].copy()
      question_data = question_data.sort_values(by=['result.response'])
      # Create Histogram Plot / Response Table
      if actor != "any":
         currSet.append(dcc.Graph(figure=response_table(question_data)))
      else:
         curr = px.histogram(question_data, histfunc="count", x='result.response', color='result.response')
         curr.update_layout( xaxis={'categoryorder':'total descending'})
         currSet.append(dcc.Graph(figure=curr))
      # Create Scatter Plot
      curr = px.scatter(question_data, x='actor.name', y = 'result.score.scaled', color='actor.name')
      currSet.append(dcc.Graph(figure=curr))
      # Question Averages
      curr = go.Figure()
      # Average Raw Score
      curr.add_trace(go.Indicator(
         mode = 'number',
         number = {'suffix': ' points'},
         value = ( math.ceil(question_data['result.score.raw'].mean() ) ),
         title = {'text': "Average Raw Score"},
         domain = {'x': [0, 0.5], 'y': [0, 0.5]}
         ))
      # Average Scaled Score
      curr.add_trace(go.Indicator(
         mode = 'number',
         number = {'suffix': ' points'},
         value = ( question_data['result.score.scaled'].mean() ),
         title= {'text': "Average Scaled Score"},
         domain = {'x': [0, 0.5], 'y': [0.5, 1]}
         ))
      # Average Time on Each Response
      curr.add_trace(go.Indicator(
         mode = 'number', number = {'suffix': ' mins'},
         value = question_data['result.duration.seconds'].mean() / 60,
         title = {'text': "Average Time per Response"},
         domain={'x': [0.6, 1], 'y': [0, 1]}
         ))
      curr.update_layout(grid = {'rows': 3, 'columns': 2})
      currSet.append(dcc.Graph(figure=curr))
      # Append all figures relating to the question
      figures[str(temp_desc[x])] = currSet
   # Make all Question Graphs
   return figures

def topicAnalysis(lrs, module, actor="any"): # Create Topics Aggregate
   conn = get_db()
   module_topics = {}
   topics = conn.execute('SELECT question_topics.topic_id FROM question_topics LEFT JOIN module_questions ON question_topics.question_id = module_questions.question_id WHERE module_id=:module', {'module':module}).fetchall()
   questions = conn.execute('SELECT * FROM module_questions WHERE module_id:=module', {'module': module}).fetchall()
   close_db()
   # Aggregate a List of All Topics for a Module
   for topic in topics:
      if str(topic[0]) not in module_topics.keys():
         module_topics[str(topic[0])] = { 'max': 1, 'score': 0 }
      else:
         module_topics[str(topic[0])]['max'] = module_topics[str(topic[0])]['max'] + 1
   # Get all responses to a specific module
   temp = lrs.loc[(lrs['verb.display.en-US'] == "answered") ].copy()
   temp_desc = temp['object.definition.description.en-US'].unique()
   # For each question, check the last attempt only
      # Get a list of each student, filter out only the last response
   if actor == "any":
      students = temp['actor.mbox'].unique()
      for x in range(0, temp_desc.size):
         # Find responses related to current question
         dataframe = temp.loc[(temp['object.definition.description.en-US'] == temp_desc[x])].copy()
         for student in students:
            # Filter responses for a student
            dataframe = dataframe.loc[dataframe['actor.mbox'] == student].copy()
            responses = dataframe['result.extensions.http://id.tincanapi.com/extension/attempt-id'].unique()
            responses = responses.loc[responses['result.extensions.http://id.tincanapi.com/extension/attempt-id'] == attempts[-1]].copy()
            student_responses = list(responses['result.response'])
   # Check against key if its close to answer
            if check_correct(student_responses temp_desc[x]):
               question_topics = []
   # Add to topic based on what topics correlate (need to get the title similar enough)
            for topic in question_topics:
               # FIXME: Works for individual, but not for aggregate...
               module_topics[str(topic)]['score'] = module_topics[str(topic)]['score'] + 1
   return None

def createAverages(lrs, module, actor="any"): # Create End Averages
   figures = []

   temp = lrs.loc[(lrs['verb.display.en-US'] == "answered") ].copy()
   temp_desc = temp['object.definition.description.en-US'].unique()
   question_avgs =  pd.DataFrame(columns = ['desc', 'seconds', 'raw score', 'scaled score'])
   for x in range(0, temp_desc.size):
      f = open("frame-" + str(x) + ".txt", "a+")
      dataframe = temp.loc[(temp['object.definition.description.en-US'] == temp_desc[x])].copy()
      dataframe = dataframe.sort_values(by=['result.response'])
      f.write(dataframe.to_string())
      f.close()
      question_avgs.append({
         'desc': temp_desc[x],
         'seconds': dataframe['result.duration.seconds'].mean(),
         'raw score': math.ceil(dataframe['result.score.raw'].mean()),
         'scaled score': dataframe['result.score.scaled'].mean()
         }, ignore_index=True)
   # Average Seconds in Module
   fig = px.line(question_avgs, x = 'desc' , y = 'seconds', markers=True, title="Seconds Per Question")
   figures.append(dcc.Graph(figure=fig))
   # Average Raw Score in Module
   fig = px.line(question_avgs, x = 'desc' , y = 'raw score',  title="Raw Score Per Question", markers=True)
   figures.append(dcc.Graph(figure=fig))
   fig = px.line(question_avgs, x = 'desc' , y = 'scaled score', title="Scaled Score Per Question", markers=True)
   figures.append(dcc.Graph(figure=fig))
   return figures