import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    # CORS = CORS(app, response={r'/*': {'origins': '*'}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers', 'Content-Type, Authorization, true'
        )
        response.headers.add(
            'Access-Control-Allow-Methods', 'GET, PUT, DELETE, POST, OPTIONS'
        )
        response.headers.add('Acces-Control-Origin', '*')
        return response
        
    def paginate_data(list, page = 1, items=QUESTIONS_PER_PAGE):
        start = (page-1)*items
        end = start + items

        return list[start:end]

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods = ['GET'])
    def get_categories():
        try:
            category_data = Category.query.all()
            formated_categoris = [category.format() for category in category_data]
            return jsonify({
                "success": True,
                "categories": formated_categoris
            }), 200
        except:
             abort(500)

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods = ['GET'])
    def get_questions():
        try:
            questions_data = Question.query.all()
            category_data = Category.query.all()

            page = request.args.get('page', 1, type=int)

            formated_questions = [question.format() for question in questions_data]
            formated_categoris = [category.format() for category in category_data]
            paginated_formated_quesions = paginate_data(formated_questions, page)
            if not paginated_formated_quesions:
                abort(404)
            return jsonify({
                "success": True,
                "questions": paginated_formated_quesions,
                "total_quesions": len(formated_questions),
                "categoris": formated_categoris,
                "currnet_categoris": int(1)
            }), 200
        except:
            abort(400)
        
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods = ['DELETE'])
    def delete_quesions(question_id):
        try:
            question = Question.query.filter(Question.id==question_id).one_or_none()
            if question is None:
                abort(404)
            question.delete()

            questions = Question.query.order_by(Question.id).all()
            pagas = request.args.get('pagas', 1, type=int)
            start = (pagas-1)*10
            end = start+10
            formated_quesions = [question.format() for question in questions]


            return jsonify({
                "success": True,
                "deleted": question_id,
                "questions": formated_quesions[start:end],
                "total_quesions": len(formated_quesions)
            }), 200
        except:
            abort(422)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions/create", methods = ['POST'])
    def create_question():
        try:
            body = request.get_json()
            new_quesion = Question(
                question = body.get('questions', None),
                answer = body.get('answer', None),
                category = body.get('category', None),
                difficulty = body.get('difficulty' , None)
            )
            new_quesion.insert()

            questions = Question.query.join(Category, Question.category==Category.id).all()
            page = request.args.get('pages', 1, type=int)
            start = (page-1)*10
            end = start+10
            formated_quesions = [quesion.format() for quesion in questions]

            category_data = Category.query().all()
            formated_catefory = [category.format() for category in category_data]

            return jsonify({
                "success": True,
                "questions": formated_quesions[start:end],
                "total_quesions": len(formated_quesions),
                "categorys": formated_catefory,
                "currnet_categoris": formated_quesions.type
            })
        except:
            abort(422)
    """
    # @TODO:
    # Create a POST endpoint to get questions based on a search term.
    # It should return any questions for whom the search term
    # is a substring of the question.

    # TEST: Search by any phrase. The questions list will update to include
    # only question that include that string within their question.
    # Try using the word "title" to start.
    # """
    @app.route('/questions/search', methods = ['POST'])
    def search_question():
        try:
            body = request.get_json()
            search = body.get_json().get('search_Term', '')
            search_qustion = Question.query.filter(Question.question.ilike('%' + search + '%')).all()

            page = request.args.get('pages', 1, type=int)
            start = (page-1) *10
            end = page + 10
            return jsonify({
                "success": True,
                "questions": search_qustion[start:end],
                "totol_questions": len(search_qustion)
            }), 200
        except:
            abort(404)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods = ['GET'])
    def get_question(category_id):
        try:
            category_questions = Question.query.filter(Question.category  == category_id).all()
            page = request.args.get('page', 1, type=int)
            start = (page-1)*10
            end = start+10
            formated_category_questions = [category_question.format() for category_question in category_questions ]
            if not formated_category_questions:
                abort(404)
            return jsonify({
                "success": True,
                "questions": formated_category_questions[start:end],
                "total_quesions": len(formated_category_questions)
            }), 200
        except:
            abort(404)
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods = ['POST'])
    def get_question_to_play():
        try:
            questions = Question.query.all()
            prev_questions = request.get_json().get('previous_questions')
            quiz_category = request.get_json().get('quiz_category')
            category_filterd_questions = Question.query.filter(Question.category == quiz_category['id']).all()

            if prev_questions is None or quiz_category is None:
                abort(404)
            if quiz_category['id'] == 0:
                category_questions = [question.format() for question in questions]
            else:
                category_questions = [question.format() for question in category_filterd_questions]
            
            while True:
                random_question = random.choice(category_questions)
                if random_question['id'] not in prev_questions:
                    break
                else:
                    return jsonify({
                        "success": True,
                        "questinos": random_question
                    }), 200
            return jsonify({
                "success": True,
                "questions": random_question
            }), 200
        except:
            abort(404)
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not found'
        }), 404
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422
    @app.errorhandler(400)
    def bad_requests(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad requests"
        }), 400
    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "success": 500,
            "message": "server error"
        }), 500
    return app

