import json
import numpy
import sys
import pandas as pd
import plotly as plotly
import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px
from pandas import json_normalize
from types import SimpleNamespace
sys.path.append('../src')
from src.db import get_db, close_db
from src.dash.topics import topics as def_topics
import sqlite3

# Add default theming
#pio.templates.default = "plotly_dark"

# Deletes extraneous data, fixes datetime strings, and aggregates module-specific data
def filter_df(dataframe, module, actor):
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
    # Stores Minimum Possible Score (If Available)
    del dataframe['result.score.min']


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
    return dataframe
def check_correct(student_answers, answers):
    # Answer Size must match!
    if len(student_answers) != len(answers):
        return False
    # Matching sizes, compare each answer
    for curr in range(0, len(student_answers)):
        currCorrect = False
        # Iterate Through Separate Strings
        for search in range(0, len(answers)):
            i = 0
            j = 0
            while i < len(student_answers[curr]) and j < len(answers[search]):
                # Found a Match
                if student_answers[curr][i].lower() == answers[search][j].lower():
                    i = i + 1
                    j = j + 1
                # No Match, Keep Looking
                else:
                    j = j + 1
            # While Loop Finished
            if i >= len(student_answers[curr]):
                currCorrect = True # Match was Found
                break # Break Out of Lexiconical Loop
        if not currCorrect: # Check If Broken or Ended
            # print("Incorrect") # Ended, Could Not Find Match
            return False
    # Finished Successfully
    # print("Correct")
    return True
def student_graphs(module_topics, responses, question, section, index):
    answers = question.answer
    # Show Responses for Each Attempt
    temp = responses.sort_values(by=['result.extensions.http://id.tincanapi.com/extension/attempt-id'])
    fig = px.histogram(temp, histfunc="count", x='result.extensions.http://id.tincanapi.com/extension/attempt-id', color='result.response')
    fig.update_layout(xaxis={'categoryorder':'total descending'})
    fig.update_layout(title="Responses for " + section + " Q"  + str(index + 1))
    # Check only last attempt
    attempts = responses['result.extensions.http://id.tincanapi.com/extension/attempt-id'].unique()
    responses = responses.loc[responses['result.extensions.http://id.tincanapi.com/extension/attempt-id'] == attempts[-1]].copy()
    # Get Student Responses
    student_answers = list(responses['result.response'])
    # Compare If It Is Correct
    if check_correct(student_answers, answers):
        for topic in question.topics:
            # Aggregate Learning Objective Score GLOBALLY
            module_topics[str(topic)]['score'] = module_topics[str(topic)]['score'] + 1
    return fig

# Creates the data based on module chosen
def create_data(value, actor="any"):
    # Get Questions from Database
    #f = open("dat_log.txt", "w")
    # Use in Production Build!
    conn = get_db()
    module_questions = conn.execute("SELECT questions FROM modules WHERE name=:module", {'module': value}).fetchall()
    close_db()

    # Use in Debug Build!
    """
    conn = sqlite3.connect('flaskr.db', detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    module_questions = conn.execute("SELECT questions FROM modules WHERE name=:module", {'module': value}).fetchall()
    conn.close()
    """
    # Parse JSON Question String Into Python Object
    if module_questions[0][0] == None:
        raise Exception("Failed to get correct module")
    fetched_questions = json.loads(str(module_questions[0][0]), object_hook=lambda d: SimpleNamespace(**d))
    # Build Set of Module Topics + Sort Questions
    concept_questions = []
    tyu_questions = []
    final_questions = []
    module_topics = {}
    for question in fetched_questions:
        if "Concept" in str(question.section):
            concept_questions.append(question)
        elif "Test Your Understanding" in str(question.section):
            tyu_questions.append(question)
        elif "Final" in str(question.section):
            final_questions.append(question)
        for topic in question.topics:
            if str(topic) not in module_topics:
                module_topics[str(topic)] = {'max': 1, 'score': 0 }
            else:
                module_topics[str(topic)]['max'] = module_topics[str(topic)]['max'] + 1
    fig_objects = []
    # Open and Parse LRS JSON
    with open('ucrstaticsw22.json') as json_file:
        xapiData = json.load(json_file)
    # Unfiltered Dataframe
    dataframe = json_normalize(xapiData)
    # Filtered Dataframe
    dataframe = filter_df(dataframe, value, actor)

    # Only the Answers Dataframe
    response_data = dataframe.loc[(dataframe['verb.display.en-US'] == "answered")].copy()
    # Use as a Questions Dictionary: The Identifier
    response_desc = response_data['object.definition.description.en-US'].unique()
    #f.write(str(response_data) + '\n')

    if actor == "any": # Instructor View : Deal with Later...
        pass
    else: # Student View : Anonymously Aggregate Data

        # question_averages = 0 # Use for time deltas?

        concept_index = 0
        tyu_index = 0
        final_index = 0
        # Create the DF with only the Actor
        response_data = response_data.loc[response_data['actor.mbox'] == actor].copy()
        # Create Graphs For Questions
        for i in range(0, response_desc.size):
            # Filter Out Anything that is not the response description
            curr_data = response_data.loc[(response_data['object.definition.description.en-US'] == response_desc[i])].copy()
            # Aggregate Answers to a Concept Quiz Question
            if "concept" in response_desc[i]:
                fig_objects.append(student_graphs(module_topics, curr_data, concept_questions[concept_index], "Concept", concept_index))
                concept_index = concept_index + 1
            # Aggregate Answers to a Test Your Understanding Quiz Question
            if "tyu" in response_desc[i]:
                fig_objects.append(student_graphs(module_topics, curr_data, tyu_questions[tyu_index], "Test Your Understanding", tyu_index))
                tyu_index = tyu_index + 1
            # Aggregate Answers to a Final Quiz Question
            if "module Q" in response_desc[i]:
                fig_objects.append(student_graphs(module_topics, curr_data, final_questions[final_index], "Final", final_index))
                final_index = final_index + 1

        # Finally... Aggregate Module Topics
        objectives = {}
        for i in module_topics.keys():
            objectives[str(def_topics[i])] = (module_topics[i]['score'] / module_topics[i]['max'])*100
        objectives = pd.DataFrame.from_dict(objectives, orient='index', columns=['Percent'])
        fig = px.bar(objectives, orientation='h', color=objectives.index)
        fig.update_layout(xaxis_title="Success Rate", yaxis_title="Objective", title="Learning Objective Performance")
        fig_objects.insert(0, fig)
        pd.set_option('display.max_columns', None)
        # print(objectives)
        #for i in fig_objects:
            #f.write(str(type(i)) + '\n')
        #f.close()
    return fig_objects
"""
    if actor is "any": # Instructor View : Aggregate Data Explicitly
        # Overall Stats Figure
        actors = dataframe.loc[dataframe['verb.display.en-US'] == "exited"].copy()

        user_stats = go.Figure()
        user_stats.add_trace(go.Indicator(
            mode = 'number',
            value = dataframe['actor.name'].nunique(),
            title = {'text': "Number of Students"},
            domain = {'row': 0, 'column': 0}
        ))
        user_stats.add_trace(go.Indicator(
            mode = 'number',
            number = {'suffix': ' mins'},
            value = (temp['result.duration.seconds'].mean() / 60),
            title = {'text': "Average Module Completion"},
            domain = {'row': 0, 'column': 1}
        ))
        user_stats.update_layout(grid = {'rows': 2, 'columns': 2})

        fig_objects.append(user_stats)

        question_averages = 0

        concept_index = 0
        tyu_index = 0
        final_index = 0
        # Create Graphs For Questions
        for i in range(0, response_desc.size):
            # Aggregate Answers to a Concept Quiz Question
            if "concept" in response_desc[i]:
                fig_objects = fig_objects + instructor_graphs(response_desc[i], module_topics, concept_index, response_data, fetched_questions)
                concept_index = concept_index + 1
            # Aggregate Answers to a Test Your Understanding Quiz Question
            if "tyu" in response_desc[i]:
                fig_objects = fig_objects + instructor_graphs(response_desc[i], module_topics, tyu_index, response_data)
                tyu_index = tyu_index + 1
            # Aggregate Answers to a Final Quiz Question
            if "module Q" in response_desc[i]:
                fig_objects = fig_objects + instructor_graphs(response_desc[i], module_topics, final_index, response_data)
                final_index = final_index + 1

def instructor_graphs(section, module_topics, index, responses):
    graphs = []
    df = responses.loc[(responses['object.definition.description.en-US'] == section)].copy()
    df = df.sort_values(by=['result.response'])
    fig = px.histogram(df, histfunc="count", x='result.response', color = 'result.response')
    fig.update_layout(xaxis={'categoryorder':'total descending'})
    fig.update_layout(title="Responses for Concept Q" + str(index + 1))
    graphs.append(fig)
    return graphs


"""

