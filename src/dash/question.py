import json
import sys
from dash import html
from types import SimpleNamespace
sys.path.append('../src')
from src.db import get_db, close_db
from src.dash.topics import topics as topicdict

def build_question(qid, slug, answers, correct, images, topics, section, number):
   if "Test Your Understanding" in section:
       return None;
   build = {
      'id': qid,
      'type': str(slug['type']),
      'body': str(slug['body']),
      'explanation': str(slug['explanation']),
      'answers': [x['answer'] for x in answers],
      'answer': [x['answer'] for x in correct],
      'images': [x['image_src'] for x in images],
      'topics': [x['title'] for x in topics],
      'section': section,
      'number': number
   }
   return build;

def create_questions(value):
   questions = []
   # DATABASE REQUEST: Grab Questions Specific to Module
   conn = get_db()
   module_questions = conn.execute("SELECT question_id, section, section_order FROM module_questions WHERE module_id=:module", {'module': value}).fetchall()
   if not module_questions:
       return None
   request = []
   for question in module_questions:
       slug = conn.execute("SELECT * FROM questions WHERE id=:question", {'question': question[0]}).fetchone()
       answers = conn.execute("SELECT answers.answer FROM answers LEFT JOIN question_answer ON answers.id=question_answer.answer_id WHERE question_answer.question_id=:question", {'question': question[0]}).fetchall()
       key_answer = conn.execute("SELECT answers.answer FROM answers LEFT JOIN answer_key ON answers.id=answer_key.correct_id WHERE answer_key.question_id=:question", {'question': question[0]}).fetchall()
       # FIXME: Use just image src paths as the ID
       images = conn.execute("SELECT images.image_src FROM images LEFT JOIN question_images ON images.id=question_images.image_id WHERE question_images.question_id=:question", {'question': question[0]}).fetchall()
       topics = conn.execute("SELECT topics.title FROM topics LEFT JOIN question_topics ON topics.id=question_topics.topic_id WHERE question_topics.question_id=:question", {'question': question[0]}).fetchall()
       if build_question(question[0], slug, answers, key_answer, images, topics, question[1], question[2]) == None:
           pass
       else:
           request.append(build_question(question[0], slug, answers, key_answer, images, topics, question[1], question[2]))
   close_db()
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
   for q in request:
       # Debugging Purposes
       # for element in ns.answer_choices:
       #    f.write(str(ns.answer) + ' ' + str(element) + '\n')

       currQuestion = []
       currQuestion.append(html.Small('Question ID: ' + str(q['id'])))
       currQuestion.append(html.H5(q['section'] + ': Question ' + str(q['number'])))
       for img in q['images']: # FIXME: Doesn't take care of image multiple choice
           currQuestion.append(html.Img(
                src='assets/' + str(img)
           ))
       currQuestion.append(html.P(q['body']))
       choices = []
       f = open('testlog.txt', 'a')
       for element in q['answer']:
           element = element.strip()
           f.write(str(q['id']))
           f.write(str(q['answer']))
           f.write(str(q['answers']))
       for element in q['answers']:
           # Correct Answer
           elementChoice = element.strip()
           if elementChoice in q['answer']:
               if "image" in elementChoice:
                    choices.append(html.Li(
                        className='correct',
                        children=html.Img(src='assets/' + str(value) + '/' + element)
                    ))
               else:
                    choices.append(html.Li(
                        className='correct',
                        children=element
                    ))
           # Fill in the Blank
           elif q['type'] == 'fb':
               continue
           # Multiple Choice Regular
           else:
               choices.append(html.Li(element))
       currQuestion.append(html.Ol(
            children=choices,
            style={ 'list-style-type':'upper-alpha' }
       ))
       if q['type'] == 'fb':
           currQuestion.append(html.P(
               className='correct',
               children=("Fill in the Blank - Correct Answer: " +', '.join(q['answer'])),
               style={ 'font-weight':'bold' }
           ))
       currQuestion.append(html.P(
           children='Explanation: ',
           style={ 'font-weight':'bold' }
       ))
       currQuestion.append(html.P(q['explanation']))
       concepts = []
       currQuestion.append(html.P(
           children='Relevant Topics:',
           style={ 'font-weight':'bold' }
       ))
       for element in q['topics']:
           concepts.append(html.Li(
               className='topic',
               children=str(element)
           ))
       currQuestion.append(html.Ul(concepts))
       questions.append(currQuestion)
       f.close()
   return questions

