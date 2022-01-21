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
   # f = open("log.txt", "w")
   for ns in parsed_json:
       # Debugging Purposes
       # for element in ns.answer_choices:
       #    f.write(str(ns.answer) + ' ' + str(element) + '\n')

       currQuestion = []
       currQuestion.append(html.H5(str(ns.section) + ': Question ' + str(i)))
       for img in ns.images:
           currQuestion.append(html.Img(
                src='assets/' + img
           ))
       currQuestion.append(html.P(ns.question))
       choices = []
       for element in ns.answer:
           element = element.strip()
       for element in ns.answer_choices:
           # Correct Answer
           elementChoice = element.strip()
           if elementChoice in ns.answer:
               choices.append(html.Li(
                    className='correct',
                    children=element
               ))
           # Fill in the Blank
           elif ns.question_type == 'fb':
               continue
           # Multiple Choice Regular
           else:
               choices.append(html.Li(element))
       currQuestion.append(html.Ol(
            children=choices,
            style={ 'list-style-type':'upper-alpha' }
       ))
       if ns.question_type == 'fb':
           currQuestion.append(html.P(
               className='correct',
               children=("Fill in the Blank - Correct Answer: " +', '.join(ns.answer)),
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
   # f.close()
   return questions

