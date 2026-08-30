from rest_framework.test import APITestCase
from rest_framework import status

from accounts.models import User

from organizations.models import Organizations


class TestUsersManage(APITestCase):

    def setUp(self):
        self.user_list_url = "/api/v1/auth/users/"


        self.organization = Organizations.objects.create(
            name="Test Organization",
            description="Test description"
        )
        

        self.system_admin = User.objects.create_user(
            username="testsystemadminuser",
            email="testsystemadmin@example.com",
            password="TestPassword123",
            is_staff=True,
            is_superuser=True
        )

        self.team_member = User.objects.create_user(
            username="testteammemberuser",
            email="testteammemberuser@example.com",
            password="TestPassword123",
            role="team_member",
        )

        self.project_manager = User.objects.create_user(
            username="testprojectmanageruser",
            email="testprojectmanageruser@example.com",
            password="TestPassword123",
            role="project_manager",
        )

        self.organization_admin = User.objects.create_user(
            username="testorganizationadminuser",
            email="testorganizationadminuser@example.com",
            password="TestPassword123",
            role="organization_admin",
        )

    def test_system_admin_can_access_users(self):
        self.client.force_authenticate(user=self.system_admin)

        response = self.client.get(self.user_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_organization_admin_can_access_users(self):
        self.client.force_authenticate(user=self.organization_admin)

        response = self.client.get(self.user_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_project_manager_cannot_access_users(self):
        self.client.force_authenticate(user=self.project_manager)

        response = self.client.get(self.user_list_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_member_cannot_access_users(self):
        self.client.force_authenticate(user=self.team_member)

        response = self.client.get(self.user_list_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_user_cannot_access_users(self):
        response = self.client.get(self.user_list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



    """ User creation Tests"""

    def test_system_admin_can_create_user(self):
        self.client.force_authenticate(user=self.system_admin)

        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "NewPassword123",
            "first_name": "New",
            "last_name": "User",
            "role": "team_member",
            "organization": self.organization.id,
        }

        response = self.client.post(
            self.user_list_url,
            data,
            format="json",
        )

        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username="newuser")

        self.assertTrue(user.check_password("NewPassword123"))

    def test_organization_admin_can_create_team_member(self):
        self.client.force_authenticate(user=self.organization_admin)

        data = {
            "username": "newmember",
            "email": "newmember@example.com",
            "password": "NewPassword123",
            "role": "team_member",
            "organization": self.organization.id,
        }

        response = self.client.post(
            self.user_list_url,
            data,
            format="json",
        )

        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_organization_admin_cannot_create_organization_admin(self):
        self.client.force_authenticate(user=self.organization_admin)

        data = {
            "username": "anotheradmin",
            "email": "anotheradmin@example.com",
            "password": "NewPassword123",
            "role": "organization_admin",
            "organization": self.organization.id,

        }

        response = self.client.post(
            self.user_list_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )