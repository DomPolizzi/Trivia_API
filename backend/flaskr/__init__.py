import os
from flask import (
    Flask,
    abort,
    jsonify,
    render_template,
    request,
    Response, 
    flash, 
    redirect, 
    url_for
)
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


# Paginiation of questions
def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

# Create and define application structure

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  cors = CORS(app, resources={'/': {"origins" : "*" }})
  

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response  
  

  #-------------
  #Get Requests for Questions, Categories, and Quizes
  #-------------
  
  #===================
  #==== Questions ====
  #===================

  @app.route('/questions')
  def retrieve_questions():
    selection = Question.query.all()
    # print("selection =", selection)
    current_questions = paginate_questions(request, selection)
    # print('current question: ', current_questions)
    total_questions = len(selection)
   # print('total Qs : ', total_questions)

    # categories = Category.query.all()
    categories_data= {}


    if len(current_questions) == 0:
      abort(404)

    return jsonify({  
        'success':True,
        'questions': current_questions,
        'total_questions': total_questions,
        'categories': categories_data
      })
  
  #===================
  #=== Categories ====
  #===================
    
  @app.route('/categories')
  def retrieve_categories():
    categories = Category.query.all()
    categories_data= {}
    
    for category in categories:
      categories_data[category.id] = category.type

    if len(categories_data) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'categories': categories_data
    })

  #----------------------------
  # GET  Question by Category
  #----------------------------

  @app.route('/categories/<int:category_id>/question')
  def get_questions_by_categories(category_id):
    category = Category.query.filter(Category.id == category_id).one_or_none()
    selection = Question.query.filter(Question.id == question_id).one_or_none()
    current_questions = paginate_questions(request, selection)
    total_questions = len(selection)

    if category is None:
      print('error')
      abort(400)
    
    else:
      print('success')
      return jsonify({
        'success': True,
        'question': current_questions,
        'total_questions': total_questions,
        'category': category.type
      })
  #CATEGORIES IS NOT YET BEING CORECTLY CALLED FOR!

  #===================
  #===== Quizzes =====
  #===================
  '''
  @app.route('/quizzes')
  def get_quizes():
    selection = Category.query.all()
    categiry_data = {}

   if len(categories_data) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'categories': categories_data
    })
  '''
  # SIDE NOTE: Enabling breaks, Quizzes needs to call from categories

  #----------------------------
  # POST Requests for Questions
  #----------------------------

  @app.route('/questions', methods=['POST'])
  def create_question():
  
    body = request.get_json()
    print('body', body)

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)
    search = body.get('search', None)

    try:
      if search:
        selection = Question.query.order_by(Question.id).filter(Question.title.ilite('%{}%'.format(search)))
        current_questions = paginate_questions(request, selection)

       
        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(selection.all())
        })

      else:
        question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
        question.insert()

        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        print('here2')
        created_id = question.id

        total_questions = len(Question.query.all())

        print("Current questions", current_questions, type(current_questions))
        print("Total questions", total_questions, type(total_questions))
        print("Created ID",  created_id, type(created_id))

        return jsonify({
          "success": True,
          "created": created_id,
          "questions": current_questions,
          "total_questions": total_questions
        })

    except:
      print('abort')
      abort(422)

  #-------------
  #Patch Request
  #-------------
  '''  
  @app.route('/questions/<int:question_id>', methods=['PATCH'])
  def update_question(question_id):

    body = request.get_json()

    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      if question is None:
        abort(404)

      if 'category' in body:
        question.category = int(body.get('category'))

      if 'difficulty' in body:
        question.category = int(body.get('difficulty'))

      if 'answer' in body:
        question.category = int(body.get('answer'))

      question.update()

      return jsonify({
        'success': True,
        'id': question.id
      })

    except:
      abort(400)
  '''
  #-------------
  #DELETE Question
  #-------------

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):      
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      else:
        question.delete()
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        created_id = question.id

        total_questions = len(Question.query.all())
        
        return jsonify({
          'success': True,
          'deleted': created_id,
          'question': current_questions,
          'total_questions': total_questions
        })
          
    except:
      abort(422)


# =================================================================
#  Error Handlers
# =================================================================

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "not found"
    }), 404

  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "unprocessable "
    }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request"
    }), 400
  
  @app.errorhandler(405)
  def not_allowed(error):
    return jsonify({
      "success": False,
      "error": 405,
      "message": "not allowed"
    }), 405

  return app


#===========================
# TO DOS
#===========================
'''

  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  
'''

'''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
 
'''

'''

  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
'''

'''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
'''

'''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
'''

'''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
'''

'''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
'''