import unittest
from starlette.testclient import TestClient
from api_server import app
from backend.db.db import Base, engine
from backend.models.user_model import User

class TestAuthRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure the users table is created before any tests run
        Base.metadata.create_all(bind=engine)

    def setUp(self):
        self.client = TestClient(app)
        self.test_user = {
            "username": "testuser@example.com",
            "password": "TestP@ssword2"
        }

    def test_1_signup_user(self):
        response = self.client.post("/signup", json=self.test_user)
        self.assertIn(response.status_code, [200, 400])  # 400 if user already exists

    def test_2_login_user(self):
        response = self.client.post("/login", json=self.test_user)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())
