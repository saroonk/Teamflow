from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


from accounts.models import User


class User_authentication_Test(APITestCase):

    def setUp(self):
        self.login_url = "/api/v1/auth/login/"

        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            role="team_member",
        )

    def test_successful_login(self):
        response = self.client.post(
            self.login_url,
            {
                "email": "test@example.com",
                "password": "TestPassword123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_login_with_wrong_password(self):
        response = self.client.post(
            self.login_url,
            {
                "email": "test@example.com",
                "password": "WrongPassword",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    
    def test_login_with_wrong_email(self):
        response = self.client.post(
            self.login_url,
            {
                "email": "wrong@example.com",
                "password": "TestPassword123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



    def test_login_without_email(self):
        response = self.client.post(
            self.login_url,
            {
                "password": "TestPassword123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_without_password(self):
        response = self.client.post(
            self.login_url,
            {
                "email": "test@example.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inactive_user_cannot_login(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            self.login_url,
            {
                "email": "test@example.com",
                "password": "TestPassword123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)