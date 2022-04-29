import re
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
from src.__init__ import mongo

def studentFilter(lrs_copy, questions, module_topics, module, student):
   # Filter By Student
   dataframe = lrs_copy.loc[lrs_copy['actor.mbox'] == student].copy()
   for i in range(0, questions.size):
      # Filter By Current Question
      curr_data = dataframe.loc[(dataframe['object.definition.description.en-US'] == questions[i])].copy()
      # Get List of attempts
      attempts = list(curr_data['result.extensions.http://id.tincanapi.com/extension/attempt-id'].unique())
      # Get Last Attempt Only
      if not attempts: # User didn't complete the question
         continue
      student_answers = curr_data.loc[curr_data['result.extensions.http://id.tincanapi.com/extension/attempt-id'] == attempts[-1]].copy()
      # Extract Response Attribute Only
      student_answers = list(student_answers['result.response'])
      # Compare Answers
      result = checkCorrect(student_answers, questions[i], module)
      if result[0]: # Correct, have to update the DB
         conn = get_db()
         topics = conn.execute('SELECT topic_id FROM question_topics WHERE question_id=:id', {'id': result[1]}).fetchall()
         close_db()
         for topic in topics: # Increment a Student's Score
            module_topics[str(topic[0])]['scores'] = module_topics[str(topic[0])]['scores'] + 1
      # Add to the average, and reset the score for the next student
   for key in module_topics.keys():
      module_topics[key]['averages'] = module_topics[key]['averages'] + (module_topics[key]['scores'] / module_topics[key]['max'])
      module_topics[key]['scores'] = 0
   return module_topics

def findQuestion(desc, module):
   description = ""
   number = int(re.sub("\D", "", desc))
   if "concept" in desc:
      description = "Concept Quiz"
   elif "module" in desc:
      description = "Final Quiz"
   #FIXME: There's 2 Kinds of TYUs!!!
   else:
      description = "Test Your Understanding"
   # Select the question
   conn = get_db()
   # Left join module_questions table with description + number parameters
   question = conn.execute("SELECT questions.id FROM questions LEFT JOIN module_questions ON questions.id = module_questions.question_id WHERE module_id=:module AND section=:description AND section_order=:num",
      {'module': module, 'description': description, 'num': number}).fetchone()
   close_db()
   return question[0]

def checkCorrect(student_answers, desc, module):
   # Find question that matches descriptor
   question_id = findQuestion(desc, module)
   conn = get_db()
   answers = conn.execute("SELECT answers.answer FROM answers LEFT JOIN answer_key ON answers.id = answer_key.correct_id WHERE answer_key.question_id=:question", {'question': question_id}).fetchall()
   close_db()
   # Find answer key that matches question
   if len(student_answers) != len(answers):
      return [False, -1]
   # Compare lists (true / false)
      for curr in range(0, len(student_answers)):
         currCorrect = False
         # Iterate Through Strings
         for search in range(0, len(answers)):
            i = 0
            j = 0
            while i < len(student_answers[curr]) and j < len(answers[search][0]):
               if student_answers[curr][i].lower() == answers[search][0][j].lower():
                  i = i + 1
                  j = j + 1
               else:
                  j = j + 1
            # While Loop Finished
            if i >= len(student_answers[curr]):
               currCorrect = True
               break
         if not currCorrect: # Check if broken or ended
            return [False, -1]
   return [True, question_id]

def parse_lrs(module, actor="any"): # Parses out the LRS
   # Open and Parse LRS JSON
   # with open('ucrstaticsw22.json') as json_file:
   #    xapiData = json.load(json_file)

   # lrs = json_normalize(xapiData)
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
   #conn = get_db()
   #module = conn.execute('SELECT name FROM modules WHERE id=:module', {'module': module}).fetchone()
   #close_db()
   if actor != any:
      lrs = mongo.db.lrs.find({"object.definition.en-US": str(module), "actor.mbox": actor})
   else:
      lrs = mongo.db.lrs.find({"object.definition.en-US": str(module)})

   # ISO8601 Parser (Maybe a Library that Does this?)
   for x in lrs["result.duration"]:
       # Parse Hours
       if 'H' in lrs['result.duration']:
           time_string = lrs['result.duration']
           lrs['result.duration'] = pd.to_datetime(lrs['result.duration'], format='PT%HH%MM%SS').time()
       # Parse Minutes
       elif 'M' in lrs['result.duration']:
           time_string = lrs['result.duration']
           lrs['result.duration'] = pd.to_datetime(lrs['result.duration'], format='PT%MM%SS').time()
       # Parse Seconds
       else:
           time_string = lrs['result.duration']
           lrs['result.duration'] = pd.to_datetime(lrs['result.duration'], format='PT%SS').time()

   # %%
   # create time delta from datetime.time objects
   lrs['result.duration.seconds'] = 'NaN'

   for x in lrs["result.duration"]:
       time_string = lrs['result.duration']
       lrs['result.duration.seconds'] = pd.to_timedelta(time_string.strftime( format="%H:%M:%S")).total_seconds()

   return lrs

def unique_actors(lrs, module): # For Instructor Only: Get Unique Actors for Module
   # Note, we passed in ID, might wanna get actual name from DB...
   # conn = get_db()
   # module = conn.execute('SELECT name FROM modules WHERE id=:module', {'module': module}).fetchone()
   # close_db()

   fig = go.Figure()

   fig.add_trace(go.Indicator(
       mode = 'number',
       value = mongo.db.lrs.distinct("actor.name").count(),
       title = {'text': "unique actors"},
        domain = {'row': 0, 'column': 0}
       ))
   # FIXME: How to filter correctly?
   temp = mongo.db.lrs.find({"object.definition.name.en-US": str(module), "verb.display.en-US": "answered"})

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

def response_table(lrs, actor):
   data = mongo.db.lrs.find({"verb.display.en-US": "answered", "actor.mbox": str(actor)}).sort()
   fig = go.Figure(data=[go.Table(
      header=dict(values=['Attempt Number', 'Response', 'Duration'], align='center'),
      cells=dict(values=[data['result.extensions.http://id.tincanapi.com/extension/attempt-id'], data['result.response'], data['result.duration.seconds']], align='center'))
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
   topics = conn.execute('SELECT topic_id FROM question_topics LEFT JOIN module_questions ON question_topics.question_id=module_questions.question_id WHERE module_id=:module', {'module': module}).fetchall()
   close_db()
   # Aggregate a List of All Topics for a Module
   for topic in topics:
      if str(topic[0]) not in module_topics.keys():
         module_topics[str(topic[0])] = { 'max': 1, 'scores': 0,'averages': 0 }
      else:
         module_topics[str(topic[0])]['max'] = module_topics[str(topic[0])]['max'] + 1
   # Get all responses to a specific module
   temp = lrs.loc[(lrs['verb.display.en-US'] == "answered")].copy()
   temp_desc = temp['object.definition.description.en-US'].unique()

   # Instructor View: Multiply by number of students to get an overall
   if actor == "any":
      num_students = temp['actor.name'].nunique()
   # For each question, check the last attempt only
      # Get a list of each student, filter out only the last response
      students = temp['actor.mbox'].unique()
      for i in range(0, len(students)):
         module_topics = studentFilter(temp, temp_desc, module_topics, module, students[i])
      pass
   # Student Objective Check
   else:
      num_students = 1
      module_topics = studentFilter(temp, temp_desc, module_topics, module, actor)
      f = open("topics.txt", "a+")
      f.write(str(module_topics))
      f.close()
   objectives = {}
   for i in module_topics.keys():
      objectives[str(def_topics[i])] = (module_topics[i]['averages'] / num_students) * 100
   objectives = pd.DataFrame.from_dict(objectives, orient='index', columns=['Percent'])
   fig = px.bar(objectives, orientation='h', color=objectives.index)
   fig.update_layout(xaxis_title="Success Rate", yaxis_title="Topic", title="Topic Performance")
   return dcc.Graph(figure=fig)

#FIXME: Does not work??
def createAverages(lrs, module, actor="any"): # Create End Averages
   figures = []
   f = open("avg.log", "w")
   temp = lrs.loc[(lrs['verb.display.en-US'] == "answered") ].copy()
   temp_desc = temp['object.definition.description.en-US'].unique()
   question_avgs =  pd.DataFrame(columns = ['question', 'desc', 'seconds', 'raw score', 'scaled score'])
   for x in range(0, temp_desc.size):
      dataframe = temp.loc[(temp['object.definition.description.en-US'] == temp_desc[x])].copy()
      dataframe = dataframe.sort_values(by=['result.response'])
      curr = pd.DataFrame([[x, 
         temp_desc[x], 
         dataframe['result.duration.seconds'].mean(),
         math.ceil(dataframe['result.score.raw'].mean()),
         dataframe['result.score.scaled'].mean()]], 
         columns=['question', 'desc', 'seconds', 'raw score', 'scaled score'])
      question_avgs = question_avgs.append(curr, ignore_index=True)
      f.write("Question " + str(x) + " Seconds: " + str(dataframe['result.duration.seconds'].mean()) + "\n")
      f.write("Question " + str(x) + " Raw Score: " + str(dataframe['result.score.raw'].mean()) + "\n")
      f.write("Question " + str(x) + " Scaled Score: " + str(dataframe['result.score.scaled'].mean()) + "\n")
   f.write(question_avgs.to_string())
   f.close()
   # Average Seconds in Module
   fig = px.line(question_avgs, x = 'question' , y = 'seconds', markers=True, title="Seconds Per Question")
   figures.append(dcc.Graph(figure=fig))
   # Average Raw Score in Module
   fig = px.line(question_avgs, x = 'question' , y = 'raw score',  title="Raw Score Per Question", markers=True)
   figures.append(dcc.Graph(figure=fig))
   fig = px.line(question_avgs, x = 'question' , y = 'scaled score', title="Scaled Score Per Question", markers=True)
   figures.append(dcc.Graph(figure=fig))
   return figures