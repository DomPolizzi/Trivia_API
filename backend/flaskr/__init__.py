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
    cors = CORS(app, resources={'/': {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    # -------------
    # Get Requests for Questions, Categories, and Quizes
    # -------------

    # ===================
    # ==== Questions ====
    # ===================

    @app.route('/questions')
    def retrieve_questions():

        selection = Question.query.all()
        current_questions = paginate_questions(request, selection)
        total_questions = len(selection)

        categories = Category.query.all()
        categories_data = {}

        for category in categories:
            categories_data[category.id] = category.type

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': total_questions,
            'categories': categories_data
        })

    # ===================
    # === Categories ====
    # ===================

    @app.route('/categories')
    def retrieve_categories():
        categories = Category.query.all()
        categories_data = {}

        for category in categories:
            categories_data[category.id] = category.type

        if len(categories_data) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': categories_data
        })

    # ----------------------------
    # GET  Question by Category
    # ----------------------------

    @app.route('/categories/<int:id>/questions')
    def get_questions_by_categories(id):
        category = Category.query.filter_by(id=id).one_or_none()

        if category is None:
            abort(400)

        selection = Question.query.filter_by(category=category.id).all()
        current_questions = paginate_questions(request, selection)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'category': category.type
        })
    # CATEGORIES IS NOT YET BEING CORECTLY CALLED FOR!

    # ===================
    # ===== Quizzes =====
    # ===================

    @app.route('/quizzes', methods=['POST'])
    def get_quizes():

        body = request.get_json()
        category_data = body.get('quiz_category')
        previous = body.get('previous_questions')

        if ((category_data is None) or (previous is None)):
            abort(400)

        if category_data['id'] == 0:
            questions = Question.query.all()

        else:
            questions = Question.query.filter_by(
                category=category_data['id']).all()

        def get_random_question():
            return questions[random.randrange(0, len(questions), 1)]

        question = get_random_question()

        return jsonify({
            'success': True,
            'question': question.format()
        })

    # ----------------------------
    # POST Requests for Questions & Search
    # ----------------------------

    @app.route('/questions', methods=['POST'])
    def create_question():

        body = request.get_json()
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)
        search = body.get('searchTerm', None)

        try:
            if search:
                search_term = body.get('searchTerm')
                selection = Question.query.filter(
                    Question.question.ilike(f'%{search_term}%')).all()
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })

            else:
                question = Question(question=new_question, answer=new_answer,
                                    category=new_category, difficulty=new_difficulty)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)
                created_id = question.id

                total_questions = len(Question.query.all())

                return jsonify({
                    "success": True,
                    "created": created_id,
                    "question_created": question.question,
                    "questions": current_questions,
                    "total_questions": total_questions
                })

        except:
            abort(422)

    # -------------
    # DELETE Question
    # -------------

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

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
