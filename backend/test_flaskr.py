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
    def test_me(self):
        self.assertTrue(True)

    #GET, Questions
    #Endpoint: '/questions[?pages=num]', Method: GET
    def test_get_paginated_questions(self):
        res = self.client().get("/questions",follow_redirects=True)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(len(data["categories"]))
        self.assertIsNone(data["currentCategory"])


    #Endpoint: `/questions?page=num`, Method: GET
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000",follow_redirects=True)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")
    #GET, Categories:


    # Endpoint: '/categories', Method: GET
    def test_get_categories(self):
        res = self.client().get("/categories",follow_redirects=True)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    #Endpoint: '/categories/{id}', Method: GET
    def test_get_category(self):
        res=self.client().get("/categories/5",follow_redirects=True)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)

    def test_get_questions_for_category(self):
        res = self.client().get("/categories/1/questions",follow_redirects=True)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(data["currentCategory"])

    def test_get_questions_for_invalid_category(self):
        res = self.client().get("/categories/100000/questions",follow_redirects=True)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")


        # / categories /${id} / questions

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()