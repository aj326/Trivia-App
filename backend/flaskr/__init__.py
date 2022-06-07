import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
# from ..models import setup_db, Question, Category
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    """
    @DONE: Use the after_request decorator to set Access-Control-Allow
    """

    """
    @DONE:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    """
    @DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    # @app.route("/")
    @app.route("/questions/")
    def retrieve_questions():
        print("in /questions, GET")
        selection = Question.query.order_by(Question.id).all()

        # using the method .format on a Category instance lead to errors ...
        formatted_categories = {cat.id: cat.type for cat in Category.query.all()}
        # page number is handled in the flask request global variable
        # see paginate_questions
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)
        # print([category.format() for category in Category.query.all()])
        return jsonify(
            {
                'success': True,
                'questions': current_questions,
                'totalQuestions': len(selection),
                'categories': formatted_categories,
                'currentCategory': None,
            }
        )

    @app.route("/categories")
    def retrieve_categories():
        return jsonify({'success': True,
                        'categories': {cat.id: cat.type for cat in Category.query.all()}})

    @app.route("/categories/<id>")
    def retrieve_categories_bad_request(id):
        abort(422)

    @app.route("/categories/<int:cat_id>/questions")
    def retrieve_questions_for_category(cat_id):
        if Category.query.get(cat_id) is None:
            abort(404)
        questions = Question.query.filter_by(category=cat_id).all()
        return jsonify({
            'success': True,
            'questions': [q.format() for q in questions],
            'totalQuestions': len(questions),
            'currentCategory': Category.query.get(cat_id).type
        }

        )

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:id>",methods=["DELETE"])
    def delete_question(id):
        question = Question.query.get(id)
        if question is None:
            abort(404)
        try:
            question.delete()
            updated_questions = Question.query.all()
            return jsonify({
            'success': True,
            'questions': paginate_questions(request, updated_questions),
            'totalQuestions': len(updated_questions),
            'categories': {cat.id: cat.type for cat in Category.query.all()},
            'currentCategory': None,
            }
            )
        except:
            abort(422)

    """
    @DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    """
    @DONE:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/questions", methods=["POST"])
    def post_question():
        body = request.get_json()
        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_difficulty = body.get("difficulty", None)
        new_category = body.get("category", None)
        searchTerm = body.get("searchTerm", None)

        if searchTerm:
            selection = Question.query.order_by(Question.id).filter(
                Question.question.ilike("%{}%".format(searchTerm))
            )
            matching_questions = paginate_questions(request, selection)
            return jsonify({
                'success': True,
                'questions': matching_questions,
                'totalQuestions': len(selection.all()),
                'currentCategory': None,
            })
        elif new_question and new_answer and new_difficulty and new_category:
            question = Question(question=new_question, category=new_category, answer=new_answer,
                                difficulty=new_difficulty)
            question.insert()
            return jsonify(
                {
                    'success': True,
                    'question': new_question,
                    'answer': new_answer,
                    'difficulty': new_difficulty,
                    'category': new_category
                }
            )
        else:
            abort(422)

    """
    @DONE:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

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

    @app.route("/quizzes", methods=["POST"])
    def post_quiz():
        body = request.get_json()
        # As per frontend code, this is an array of question ids
        previous_questions = body.get("previous_questions", None)
        # As per frontend code, null maps to all categories
        quiz_category = body.get("quiz_category", None)
        if quiz_category['id']:
            questions_not_already_asked = Question.query.filter(Question.category == quiz_category['id']).filter(
                ~Question.id.in_(previous_questions)).all()
        else:
            questions_not_already_asked = Question.query.filter(~Question.id.in_(previous_questions)).all()
        print(questions_not_already_asked)
        if questions_not_already_asked:
            new_question = random.choice(questions_not_already_asked)
        else:
            new_question = None
        print(new_question.format() if new_question else "No more q")
        return jsonify({
            'success': True,
            'question': new_question.format() if new_question else None
        })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def resource_not_found(e):
        return jsonify({'success': False,
                        'message': 'Resource not found'}), 404

    @app.errorhandler(422)
    def unprocessable_entity(e):
        return jsonify({'success': False,
                        'message': 'Unprocessable Entity'}), 422

    return app
