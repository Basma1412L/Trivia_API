import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import Category, Question
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route
  after completing the TODOs
  '''
    CORS(app, resources=({r"/api/*": {"origins": "*"}}))
    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, POST, PATCH, DELETE, OPTIONS')
        return response
    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    @app.route('/categories')
    def retrive_categories():
        categories = Category.query.all()
        current_categories = {
            category.id: category.type for category in categories}
        if current_categories is None or len(current_categories) == 0:
            abort(404)
        length = len(current_categories)
        return jsonify({
            'success': True,
            'categories': current_categories,
            'total_categories': length
        })

    '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom
  of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
    @app.route('/questions')
    def retrive_questions():
        try:
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            # print('Current Questions', current_questions)
            if current_questions is None or len(current_questions) == 0:
                abort(404)
            # print('Getting')
            categories = Category.query.all()
            formatted_categories = {
                category.id: category.type for category in categories}
            return jsonify({
                'success': True,
                'questions': current_questions,
                'categories': formatted_categories,
                'total_questions': len(Question.query.all())
            })
        except Exception as error:
            print("\nerror => {}\n".format(error))
            abort(404)

    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.
  TEST: When you click the trash icon next to a question,
  the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            # print('deleting question_id is:', question_id)
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            if question is None:
                abort(404)
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            # print('Deleting')
            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })
        except Exception as error:
            print("\nerror => {}\n".format(error))
            abort(422)

    '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)
        # print('adding')
        try:
            if new_question and new_answer and new_category and new_difficulty:
                question = Question(
                    question=new_question,
                    answer=new_answer,
                    category=new_category,
                    difficulty=new_difficulty)
                # print(question.question)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'created': question.id,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })
            else:
                abort(404)
        except Exception as error:
            print("\nerror => {}\n".format(error))
            abort(422)

    '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
    @app.route('/questions/search', methods=['POST'])
    def search_question():
        body = request.get_json()
        search = body.get('searchTerm', None)
        try:
            if search:
                selection = Question.query.order_by(
                    Question.id).filter(
                    Question.question.ilike(
                        '%{}%'.format(search)))
                current_questions = paginate_questions(request, selection)
                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(selection.all())
                })
            else:
                abort(404)
        except Exception as error:
            print("\nerror => {}\n".format(error))
            abort(422)
    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
    @app.route('/categories/<category>/questions/')
    def retrive_category_questions(category):
        try:
            selection = Question.query.filter(
                Question.category == category).all()
            current_category = Category.query.filter(
                Category.id == category).one_or_none()
            if (current_category):
                current_category = current_category.type
            length = len(selection)
            current_questions = paginate_questions(request, selection)
            if current_questions is None or len(current_questions) == 0:
                abort(404)
            # print('Getting Category Questions')
            # print(current_category)
            # print(current_questions)
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': length,
                'current_category': current_category
            })
        except Exception as error:
            print("\nerror => {}\n".format(error))
            abort(404)

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
    @app.route('/quizzes', methods=['POST'])
    def get_questions():
        try:
            body = request.get_json()
            category = body.get('quiz_category', None)
            questions_id = body.get('previous_questions')
            # print(questions_id)
            print('Category: ', category)
            selection = Question.query.filter(
                Question.category == category['id']).all()
            print('Selection: ', selection)
            if len(selection) == 0:
                selection = Question.query.all()
            clear_selections = []
            for q in selection:
                if q.id not in questions_id:
                    clear_selections.append(q)
            print('Clear Questions:', clear_selections)
            question_random = random.choice(clear_selections)
            print('Random Question: ', question_random)
            if question_random is not None:
                return jsonify({
                    'success': True,
                    'question': question_random.format()
                })
            else:
                abort(404)
        except Exception as error:
            print("\nerror => {}\n".format(error))
            abort(404)
    '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
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
            "message": "method not allowed"
        }), 405
    return app
