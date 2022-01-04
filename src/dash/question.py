# FIXME: Questions are not writing!!

import json
import sys
from dash import html
from types import SimpleNamespace
sys.path.append('../src')
from src.db import get_db, close_db

def create_questions(value):
   questions = []
   # DATABASE REQUEST: Grab Questions Specific to Module
   conn = get_db()
   # WARNING: Unsafe!
   module_questions = conn.execute('SELECT questions FROM modules WHERE name=\"' + value + '\"').fetchall()
   close_db()
   # Parse JSON String Into Python Object
   if module_questions[0][0] == None:
       return questions
   parsed_json = json.loads(str(module_questions[0][0]), object_hook=lambda d: SimpleNamespace(**d))
   # Convert Python Object Into HTML
   # question_type: skip
   # question: H2
   # answer_choices: Ol (type="A"), Li
   # answer: bold
   # topics: Ul, Li
   # images: Img src="images[i]"
   # Put Br objects between each

   currQuestion = []
   for ns in parsed_json:
       currQuestion = []
       currQuestion.append(html.H3(ns.question))
       choices = []
       for element in ns.answer_choices:
           choices.append(html.Li(element))
       currQuestion.append(html.Ol(
            children=choices,
            style={ 'list-style-type':'upper-alpha' }
       ))
       currQuestion.append(html.P(
            children=ns.answer,
            style={ 'font-weight':'bold' }
       ))
       concepts = []
       for element in ns.topics:
           concepts.append(html.Li(element))
       currQuestion.append(html.Ul(concepts))
       for img in ns.images:
           currQuestion.append(html.Img(
                src=img
           ))
       questions.append(currQuestion)
   return questions

