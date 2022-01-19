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
   i = 1
   for ns in parsed_json:
       # Debugging Purposes
       #f = open("log.txt", "w")
       #f.write(str(ns.__dict__))
       #f.close()
       currQuestion = []
       currQuestion.append(html.H5(str(ns.section) + ': Question ' + str(i)))
       for img in ns.images:
           currQuestion.append(html.Img(
                src='assets/' + img
           ))
       currQuestion.append(html.P(ns.question))
       choices = []
       for element in ns.answer_choices:
           if element == ns.answer:
               choices.append(html.Li(
                    className='correct',
                    children=element
               ))
           else:
               choices.append(html.Li(element))
       currQuestion.append(html.Ol(
            children=choices,
            style={ 'list-style-type':'upper-alpha' }
       ))
       currQuestion.append(html.P(
           children=("Correct Answer: " +' '.join(ns.answer)),
           style={ 'font-weight':'bold' }
       ))
       currQuestion.append(html.P(
           children='Explanation: ',
           style={ 'font-weight':'bold' }
       ))
       currQuestion.append(html.P(ns.explanation))
       concepts = []
       currQuestion.append(html.P(
           children='Relevant Topics:',
           style={ 'font-weight':'bold' }
       ))
       for element in ns.topics:
           concepts.append(html.Li(
               className='topic',
               children=element
           ))
       currQuestion.append(html.Ul(concepts))
       questions.append(currQuestion)
       i = i + 1
   return questions

