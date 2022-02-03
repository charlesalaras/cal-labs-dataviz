# Code derived from https://github.com/guptaraghav29/PythonPlotly

import json
import pandas as pd
import plotly as plotly
import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px
from pandas import json_normalize
# Unsure if works
#from .db import get_db

# Add default theming
pio.templates.default = "plotly_dark"

# Creates the data based on module chosen
def create_data(module, actor="any"):

   # Open and Parse LRS JSON
   with open('sample_lrs.json') as json_file:
      xapiData = json.load(json_file)

   dataframe = json_normalize(xapiData)

   # Stores Course Link
   del dataframe['object.id']
   # Stores 'Activity'
   del dataframe['object.objectType']
   # Stores type link
   del dataframe['object.definition.type']
   # Stores Access Level
   del dataframe['authority.objectType']
   # Stores LRS Link
   del dataframe['authority.account.homePage']
   # Stores 'authorization'
   del dataframe['authority.account.name']
   # Stores verb link
   del dataframe['verb.id']
   # Stores timestamp loaded
   del dataframe['stored']
   # Stores User Email
   # del dataframe['actor.mbox']
   # Stores Minimum Possible Score (If Available)
   del dataframe['result.score.min']

   fig_objects = []
   if actor == "any":
      # Instructor View, Aggregate All Module Data
      temp = dataframe.loc[dataframe['object.definition.name.en-US'] == module].copy()
   else:
      # Student View, Aggregate Student Data for a Module
      temp = dataframe.loc[dataframe['object.definition.name.en-US'] == module].copy()
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
   dataframe = temp.copy()

   # %%
   # create time delta from datetime.time objects
   dataframe['result.duration.seconds'] = 'NaN'

   temp = dataframe.copy()
   for x in temp.index:
       time_string = temp.at [x, 'result.duration']
       temp.at[x, 'result.duration.seconds'] = pd.to_timedelta(time_string.strftime( format="%H:%M:%S")).total_seconds()
   dataframe = temp.copy()

   # Figure 1
   # Unique Actors for a Module

   fig = go.Figure()

   fig.add_trace(go.Indicator(
       mode = 'number',
       value = dataframe['actor.name'].nunique(),
       title = {'text': "unique actors"},
        domain = {'row': 0, 'column': 0}
       ))

   temp = dataframe.loc[dataframe['verb.display.en-US'] == "exited"].copy()

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

   fig_objects.append(fig)


   # Parse Questions
   # create list of answered descriptions
   temp = dataframe.loc[(dataframe['verb.display.en-US'] == "answered") ].copy()
   temp_desc = temp['object.definition.description.en-US'].unique()
   # array has been sorted


   # Question Number
   quiz_num = 0
   # Grab Score Data into DataFrame
   question_avgs =  pd.DataFrame(columns = ['question', 'desc', 'seconds','raw score', 'scaled score'])

   # ceiling function
   import math

   # make all the graphs in loop
   for x in range(0, temp_desc.size):
       # Final Quiz
       if "3." in temp_desc[x]:
           quiz_num = quiz_num + 1
           finalquiz_dataframe = temp.loc[(temp['object.definition.description.en-US'] == temp_desc[x])].copy()
           finalquiz_dataframe = finalquiz_dataframe.sort_values(by=['result.response'])
           # Create Histogram + Details
           fig = px.histogram(finalquiz_dataframe, histfunc="count", x='result.response', color='result.response')
           fig.update_layout( xaxis={'categoryorder':'total descending'})
           # FIXME: Question is Hardcoded here
           fig.update_layout(title="Responses for Final Q" + str(quiz_num))
           # Append Histogram Plot Figure
           fig_objects.append(fig)

           # Create Scatter + Details
           fig = px.scatter(finalquiz_dataframe,x='actor.name', y = 'result.score.scaled', color='actor.name')
           fig.update_layout(title="Student Scores for Final Q"  + str(quiz_num))
           # Append Scatter Plot Figure
           fig_objects.append(fig)

           # Calculate Averages of Question Scores
           question_avgs= question_avgs.append({'question': quiz_num, 'desc': temp_desc[x] , 'seconds': finalquiz_dataframe['result.duration.seconds'].mean(),
               #FIXME: Crashes if "answered" in description
                   'raw score' :  math.ceil(finalquiz_dataframe['result.score.raw'].mean() ) , 'scaled score' :  finalquiz_dataframe['result.score.scaled'].mean() },ignore_index=True )

           # Create Averages Figure
           fig = go.Figure()

           # Average Raw Score
           fig.add_trace(go.Indicator(
               mode = 'number',
               number = {'suffix': ' points'},
               value = ( (question_avgs.at[quiz_num - 1, 'raw score'] ) ),
               title = {'text': "Average Raw Score: Q" +  str(quiz_num) },
                domain = {'x': [0, 0.5], 'y': [0, 0.5]}
               ))

           # Average Scaled Score
           fig.add_trace(go.Indicator(
               mode = 'number',
               number = {'suffix': ' points'},
               value = ( question_avgs.at[quiz_num - 1, 'scaled score'] ) ,
               title = {'text':"Average scaled Score: Q" +  str(quiz_num)},
               domain = {'x': [0, 0.5], 'y': [0.5, 1]}
               ))

           # Average Time Spent on Question
           fig.add_trace(go.Indicator(
           mode = 'number', number = {'suffix': ' mins'},
           value = finalquiz_dataframe['result.duration.seconds'].mean() / 60,
           title = {'text': "Average Time: Q"  +  str(quiz_num)},
           domain={'x': [0.6, 1], 'y': [0, 1]}
           ))
           # create grid
           fig.update_layout(
               grid = {'rows': 3, 'columns': 2})

           # Append Averages Figure
           fig_objects.append(fig)

   # Create Average Completion Figure
   fig = go.Figure()
   fig.add_trace(go.Indicator(
       mode = 'number',
       number = {'suffix': ' mins'},
       value = ( question_avgs['seconds'].mean() / 60),
       title = {'text': "Avg Response"},
       domain = {'row': 0, 'column': 0}
       ))
   fig.add_trace(go.Indicator(
       mode = 'number',
       number = {'suffix': ' mins'},
       value = (( question_avgs['seconds'].sum() ) / 60) ,
       title = {'text': "Avg Quiz Completion"},
       domain = {'row': 0, 'column': 1}
       ))
   # create grid
   fig.update_layout(
       grid = {'rows': 2, 'columns': 2})

   # Append Average Completion Figure
   fig_objects.append(fig)

   # Final Aggregate Plots

   # Seconds Per Question
   fig = px.line(question_avgs, x = 'question' , y = 'seconds', markers=True, title="Seconds Per Question")

   fig_objects.append(fig)

   # Raw Score Per Question
   fig = px.line(question_avgs, x = 'question' , y = 'raw score',  title="Raw Score Per Question", markers=True)

   fig_objects.append(fig)

   # Scaled Score Per Question
   fig = px.line(question_avgs, x = 'question' , y = 'scaled score', title="scaled Score Per Question", markers=True)

   fig_objects.append(fig)

   return fig_objects

