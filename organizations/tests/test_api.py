from rest_framework.test import APITestCase
from rest_framework import status

from accounts.models import User

from organizations.models import Organizations



class OrganizationCreateAndAccessTest(APITestCase):

    def setUp(self):

        self.organization_url = "/api/v1/organizations/"


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



    def test_organization_view_only_authenticated_users(self):
        response = self.client.get(self.organization_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_system_admin_can_create_organization(self):
        
        data = {
            "name" : "new test orgo",
            "description":"hooooip"
        }

        self.client.force_authenticate(user=self.system_admin)

        response = self.client.post(
            self.organization_url,
            data,
            format="json"
        )


        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    
    def test_organization_admin_cannot_create_organization(self):
        
        data = {
            "name" : "new test orgo",
            "description":"hooooip"
        }

        self.client.force_authenticate(user=self.organization_admin)

        response = self.client.post(
            self.organization_url,
            data,
            format="json"
        )


        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    
    def test_team_member_cannot_create_organization(self):
        
        data = {
            "name" : "new test orgo",
            "description":"hooooip"
        }

        self.client.force_authenticate(user=self.team_member)

        response = self.client.post(
            self.organization_url,
            data,
            format="json"
        )


        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


