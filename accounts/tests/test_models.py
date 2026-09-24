from django.test import TestCase
from django.db import IntegrityError

from accounts.models import User


class UserModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            first_name="Test",
            last_name="User",
            role="team_member",
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.first_name, "Test")
        self.assertEqual(self.user.last_name, "User")
        self.assertEqual(self.user.role, "team_member")
        self.assertTrue(self.user.is_active)

    def test_password_is_hashed(self):
        self.assertNotEqual(
            self.user.password,
            "TestPassword123"
        )

    def test_password_is_correct(self):
        self.assertTrue(
            self.user.check_password("TestPassword123")
        )

    def test_wrong_password_is_rejected(self):
        self.assertFalse(
            self.user.check_password("WrongPassword")
        )

    def test_user_email_is_unique(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="anotheruser",
                email="test@example.com",
                password="AnotherPassword123",
                role="team_member",
            )