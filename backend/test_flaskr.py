import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('postgres:abc@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {"question": "TEST What color is the sky?",
                             "answer": "TEST blue",
                             "difficulty": 1,
                             "category": 1}
        self.new_bad_question = {"question": "TEST What color is the sky?",
                                 "difficulty": 1,
                                 "category": 1}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    # GET, Questions
    # Endpoint: '/questions[?pages=num]', Method: GET
    def test_get_paginated_questions(self):
        res = self.client().get("/questions", follow_redirects=True)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(len(data["categories"]))
        self.assertIsNone(data["currentCategory"])

    # Endpoint: `/questions?page=num`, Method: GET
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000", follow_redirects=True)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")

    # GET, Categories:
    # Endpoint: '/categories', Method: GET
    def test_get_categories(self):
        res = self.client().get("/categories", follow_redirects=True)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    # Endpoint: '/categories/{id}', Method: GET
    def test_get_category(self):
        res = self.client().get("/categories/5", follow_redirects=True)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)

    def test_get_questions_for_category(self):
        res = self.client().get("/categories/1/questions", follow_redirects=True)
        print(res.data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(data["currentCategory"])

    def test_get_questions_for_invalid_category(self):
        res = self.client().get("/categories/100000/questions", follow_redirects=True)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")

    # POST, Questions:
    def test_post_new_question(self):
        res = self.client().post("/questions", follow_redirects=True, json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])
        self.assertTrue(data["answer"])
        self.assertTrue(data["difficulty"])
        self.assertTrue(data["category"])

    def test_422_post_new_question_not_allowed(self):
        res = self.client().post("/questions", follow_redirects=True, json=self.new_bad_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable Entity")

    def test_search_for_questions(self):
        res = self.client().post("/questions", follow_redirects=True, json={"searchTerm": "Title"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['totalQuestions'])
        self.assertIsNone(data['currentCategory'])

    def test_search_for_questions_returns_no_quetions(self):
        res = self.client().post("/questions", follow_redirects=True, json={"searchTerm": "Title0000000000000"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertFalse(len(data['questions']))
        self.assertFalse(data['totalQuestions'])
        self.assertIsNone(data['currentCategory'])

    def test_quizz_with_cat(self):
        res = self.client().post("/quizzes", follow_redirects=True,
                                 json={"previous_questions": [1, 2, 3], "quiz_category": {"id": 2}})
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertTrue(data['question'])

    def test_quizz_without_cat(self):
        res = self.client().post("/quizzes", follow_redirects=True,
                                 json={"previous_questions": [1, 2, 3], "quiz_category": {"id": 0}})
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertTrue(data['question'])

    def test_delete_success(self):
        prev_res = self.client().get("/questions", follow_redirects=True)
        prev_total = (json.loads(prev_res.data))['totalQuestions']
        res = self.client().delete("/questions/16", follow_redirects=True)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data["totalQuestions"], prev_total - 1)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(len(data["categories"]))
        self.assertIsNone(data["currentCategory"])

    def test_delete_fail(self):
        res = self.client().delete("/questions/1600", follow_redirects=True)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Resource not found")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
