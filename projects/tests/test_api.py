from rest_framework.test import APITestCase
from rest_framework import status

from accounts.models import User

from organizations.models import Organizations
from projects.models import Project



class ProjectCreateAndAccessTest(APITestCase):

    def setUp(self):

        self.projects_url = "/api/v1/projects/"


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
            organization=self.organization,
        )


        self.another_project_manager = User.objects.create_user(
            username="anotherprojectmanager",
            email="anotherprojectmanager@example.com",
            password="TestPassword123",
            role="project_manager",
            organization=self.organization,
        )

        self.organization_admin = User.objects.create_user(
            username="testorganizationadminuser",
            email="testorganizationadminuser@example.com",
            password="TestPassword123",
            role="organization_admin",
        )



        self.project = Project.objects.create(
            title="Test Project",
            description="Test description",
            organization=self.organization,
            project_manager=self.project_manager,
            priority="low",
            status="planning"
        )

        self.project.team_members.add(self.team_member)



    def test_project_view_only_authenticated_users(self):
        response = self.client.get(self.projects_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_system_admin_can_create_project(self):

        data = {
            "title": "New Test Project",
            "description": "Test project description",
            "organization": self.organization.id,
            "project_manager": self.project_manager.id,
            "priority": "low",
            "status": "planning",
        }

        self.client.force_authenticate(user=self.system_admin)

        response = self.client.post(
            self.projects_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_organization_admin_can_create_project(self):

        data = {
            "title": "New Test Project",
            "description": "Test project description",
            "organization": self.organization.id,
            "project_manager": self.project_manager.id,
            "priority": "low",
            "status": "planning",
        }

        self.client.force_authenticate(user=self.organization_admin)

        response = self.client.post(
            self.projects_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



    def test_project_manager_can_create_project(self):

        data = {
            "title": "New Test Project",
            "description": "Test project description",
            
            
            "priority": "low",
            "status": "planning",
        }
    
        self.client.force_authenticate(user=self.project_manager)

        response = self.client.post(
            self.projects_url,
            data,
            format="json"
        )

        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



    def test_project_manager_cannot_create_project_for_another_project_manager(self):

        data = {
            "title": "New Test Project",
            "description": "Test project description",
            "organization": self.organization.id,
            "project_manager": self.another_project_manager.id,
            "priority": "low",
            "status": "planning",
        }

        self.client.force_authenticate(user=self.project_manager)

        response = self.client.post(
            self.projects_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



    def test_team_member_cannot_create_project(self):

        data = {
            "title": "New Test Project",
            "description": "Test project description",
            "organization": self.organization.id,
            "project_manager": self.project_manager.id,
            "priority": "low",
            "status": "planning",
        }

        self.client.force_authenticate(user=self.team_member)

        response = self.client.post(
            self.projects_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    