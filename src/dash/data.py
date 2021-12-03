# Code pulled from https://github.com/guptaraghav29/PythonPlotly

# %% [markdown]
# # Moudule 12 Course Data
# 
# ---
# 

# %%
import json
import pandas as pd
import plotly as plotly
import plotly.graph_objects as go
import plotly.express as px
from pandas import json_normalize

with open('sample_lrs.json') as json_file:
    xapiData = json.load(json_file)

#https://www.delftstack.com/howto/python-pandas/json-to-pandas-dataframe/
df = json_normalize(xapiData)

# %%
# below feilds are all the same, english version of other feilds, or too general to be usefull right now. These feilds can be edited in revisons to xAPI
# del trimmed_df['id'] actually keep this, we can use this with the ip CSV
del df['object.id']
del df['object.objectType']
del df['authority.objectType']
del df['authority.account.homePage']
del df['authority.account.name']
del df['verb.id']
del df['stored']
del df['actor.mbox']
del df['object.definition.type']
del df['result.score.min']
# trimmed_df.reset_index(drop=True, inplace=True)

fig_objects= []

# %%
# lets deal wiht module 12 data
# 
temp = df.loc[df['object.definition.name.en-US'] == "Week 5 Module 12: Friction"].copy()
for x in temp.index:
    if 'H' in temp.at[x, 'result.duration']:
       # print(x)
        time_string = temp.at [x, 'result.duration']
        #print(time_string)
        temp.at[x, 'result.duration'] = pd.to_datetime(temp.at[x, 'result.duration'], format='PT%HH%MM%SS').time()
       # print(temp.at[x, 'result.duration'] )
    elif 'M' in temp.at[x, 'result.duration']:
       # print(x)
        time_string = temp.at [x, 'result.duration']
        #print(time_string)
        temp.at[x, 'result.duration'] = pd.to_datetime(temp.at[x, 'result.duration'], format='PT%MM%SS').time()
        #print(temp.at[x, 'result.duration'] )
    else:
        #print(x)
        time_string = temp.at [x, 'result.duration']
       # print(time_string)
        temp.at[x, 'result.duration'] = pd.to_datetime(temp.at[x, 'result.duration'], format='PT%SS').time()
        #print(temp.at[x, 'result.duration'] )
df = temp.copy()

# %%
# create time delta from datetime.time objects 
df['result.duration.seconds'] = 'NaN'

temp = df.copy()
for x in temp.index:
    #print(x)
    time_string = temp.at [x, 'result.duration']
   # print(time_string)
    temp.at[x, 'result.duration.seconds'] = pd.to_timedelta(time_string.strftime( format="%H:%M:%S")).total_seconds()
    #print(temp.at[x, 'result.duration.seconds'] )
df = temp.copy()

# %%
# Dataframe.col_name.nunique()

fig = go.Figure()

fig.add_trace(go.Indicator(
    mode = 'number',
    value = df['actor.name'].nunique(),
    title = {'text': "unique actors"},
     domain = {'row': 0, 'column': 0}
    ))
# 
temp = df.loc[df['verb.display.en-US'] == "exited"].copy()
#

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

#
fig_objects.append(fig)
#



# %%
# create list of answered descriptions
temp = df.loc[(df['verb.display.en-US'] == "answered") ].copy()
temp_desc = temp['object.definition.description.en-US'].unique()
# array has been sorted


# %%
quiz_num = 0
print(temp_desc.size)
question_avgs =  pd.DataFrame(columns = ['question', 'desc', 'seconds','raw score', 'scaled score'])

import math  

# make all the graphs at once
for x in range(0, temp_desc.size):
    if "3." in temp_desc[x]:
        quiz_num = quiz_num + 1
        print(temp_desc[x])
        finalquiz_df = temp.loc[(temp['object.definition.description.en-US'] == temp_desc[x])].copy()
        #finalquiz_df.head()
        # sort by
        finalquiz_df = finalquiz_df.sort_values(by=['result.response'])
        # create graphs
        fig = px.histogram(finalquiz_df, histfunc="count", x='result.response', color='result.response')
        fig.update_layout( xaxis={'categoryorder':'total descending'})
        fig.update_layout(title="Responses for Final Q" + str(quiz_num))
        fig_objects.append(fig)
        
        fig = px.scatter(finalquiz_df,x='actor.name', y = 'result.score.scaled', color='actor.name')
        fig.update_layout(title="Student Scores for Final Q"  + str(quiz_num))
        fig_objects.append(fig)
        
       
        question_avgs= question_avgs.append({'question': quiz_num, 'desc': temp_desc[x] , 'seconds': finalquiz_df['result.duration.seconds'].mean(), 
                'raw score' :  math.ceil(finalquiz_df['result.score.raw'].mean() ) , 'scaled score' :  finalquiz_df['result.score.scaled'].mean() },ignore_index=True )
        ###
        fig = go.Figure()

        fig.add_trace(go.Indicator(
            mode = 'number',
            number = {'suffix': ' points'},
            value = ( (question_avgs.at[quiz_num - 1, 'raw score'] ) ),
            title = {'text': "Average Raw Score: Q" +  str(quiz_num) },
             domain = {'x': [0, 0.5], 'y': [0, 0.5]}
            ))

        fig.add_trace(go.Indicator(
            mode = 'number',
            number = {'suffix': ' points'},
            value = ( question_avgs.at[quiz_num - 1, 'scaled score'] ) ,
            title = {'text':"Average scaled Score: Q" +  str(quiz_num)},
            domain = {'x': [0, 0.5], 'y': [0.5, 1]}
            ))

        fig.add_trace(go.Indicator(
        mode = 'number', number = {'suffix': ' mins'},
        value = finalquiz_df['result.duration.seconds'].mean() / 60,
        title = {'text': "Average Time: Q"  +  str(quiz_num)},
        domain={'x': [0.6, 1], 'y': [0, 1]}
        ))
        # create grid    
        fig.update_layout(
            grid = {'rows': 3, 'columns': 2})
        
        fig_objects.append(fig)

        
        

     #   fig.add_trace(go.Indicator(
    #        mode = 'number', number = {'suffix': ' mins'},
   #         value = finalquiz_df['result.duration.seconds'].mean() / 60,
  #          title = {'text': "Average Time"}
 #           ))
#        fig.show()



# %%
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

#
fig_objects.append(fig)



fig = px.line(question_avgs, x = 'question' , y = 'seconds', markers=True, title="Seconds Per Question")

fig_objects.append(fig)


fig = px.line(question_avgs, x = 'question' , y = 'raw score',  title="Raw Score Per Question", markers=True)

fig_objects.append(fig)


fig = px.line(question_avgs, x = 'question' , y = 'scaled score', title="scaled Score Per Question", markers=True)

fig_objects.append(fig)




