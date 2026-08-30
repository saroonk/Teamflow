from rest_framework.test import APITestCase
from rest_framework import status

from accounts.models import User
from organizations.models import Organizations
from projects.models import Project
from tasks.models import Task


class TaskCreateAndAccessTest(APITestCase):

    def setUp(self):

        self.tasks_url = "/api/v1/tasks/"

        # Organization
        self.organization = Organizations.objects.create(
            name="Test Organization",
            description="Test description"
        )

        # Users
        self.system_admin = User.objects.create_user(
            username="testsystemadmin",
            email="systemadmin@example.com",
            password="TestPassword123",
            is_staff=True,
            is_superuser=True
        )

        self.organization_admin = User.objects.create_user(
            username="testorganizationadmin",
            email="organizationadmin@example.com",
            password="TestPassword123",
            role="organization_admin",
            organization=self.organization,
        )

        self.project_manager = User.objects.create_user(
            username="testprojectmanager",
            email="projectmanager@example.com",
            password="TestPassword123",
            role="project_manager",
            organization=self.organization,
        )

        self.another_project_manager = User.objects.create_user(
            username="anotherprojectmanager",
            email="anothermanager@example.com",
            password="TestPassword123",
            role="project_manager",
            organization=self.organization,
        )

        self.team_member = User.objects.create_user(
            username="testteammember",
            email="teammember@example.com",
            password="TestPassword123",
            role="team_member",
            organization=self.organization,
        )

        self.another_team_member = User.objects.create_user(
            username="anotherteammember",
            email="anotherteammember@example.com",
            password="TestPassword123",
            role="team_member",
            organization=self.organization,
        )

        # Projects
        self.project = Project.objects.create(
            title="Project One",
            description="Project one",
            organization=self.organization,
            project_manager=self.project_manager,
            priority="low",
            status="planning",
        )

        self.another_project = Project.objects.create(
            title="Project Two",
            description="Project two",
            organization=self.organization,
            project_manager=self.another_project_manager,
            priority="medium",
            status="planning",
        )

        self.project.team_members.add(self.team_member)
        self.another_project.team_members.add(self.another_team_member)

        # Tasks
        self.task = Task.objects.create(
            title="Task One",
            description="Task one description",
            project=self.project,
            assigned_to=self.team_member,
            created_by=self.project_manager,
            priority="medium",
            status="planning",
        )

        self.another_task = Task.objects.create(
            title="Task Two",
            description="Task two description",
            project=self.another_project,
            assigned_to=self.another_team_member,
            created_by=self.another_project_manager,
            priority="medium",
            status="planning",
        )

        self.task_detail_url = f"{self.tasks_url}{self.task.id}/"
        self.another_task_detail_url = (
            f"{self.tasks_url}{self.another_task.id}/"
        )


    

    def test_unauthenticated_user_cannot_view_tasks(self):

        response = self.client.get(self.tasks_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


    def test_system_admin_can_view_all_tasks(self):

        self.client.force_authenticate(user=self.system_admin)

        response = self.client.get(self.tasks_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(len(response.data), 2)


    def test_organization_admin_can_view_all_tasks(self):

        self.client.force_authenticate(user=self.organization_admin)

        response = self.client.get(self.tasks_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(len(response.data), 2)



    def test_project_manager_can_only_view_tasks_from_own_projects(self):

        self.client.force_authenticate(user=self.project_manager)

        response = self.client.get(self.tasks_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        task_ids = [task["id"] for task in response.data]

        self.assertIn(self.task.id, task_ids)
        self.assertNotIn(self.another_task.id, task_ids) 


    def test_team_member_can_only_view_assigned_tasks(self):

        self.client.force_authenticate(user=self.team_member)

        response = self.client.get(self.tasks_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        task_ids = [task["id"] for task in response.data]

        self.assertIn(self.task.id, task_ids)
        self.assertNotIn(self.another_task.id, task_ids)




    def test_unauthenticated_user_cannot_create_task(self):

        data = {
            "title": "New Task",
            "description": "New task description",
            "project": self.project.id,
            "assigned_to": self.team_member.id,
            "priority": "medium",
            "status": "planning",
        }

        response = self.client.post(
            self.tasks_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


    def test_team_member_cannot_create_task(self):

        data = {
            "title": "New Task",
            "description": "New task description",
            "project": self.project.id,
            "assigned_to": self.team_member.id,
            "priority": "medium",
            "status": "planning",
        }

        self.client.force_authenticate(user=self.team_member)

        response = self.client.post(
            self.tasks_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )



    def test_project_manager_can_create_task_on_own_project(self):

        data = {
            "title": "New Task",
            "description": "New task description",
            "project": self.project.id,
            "assigned_to": self.team_member.id,
            "priority": "medium",
            "status": "planning",
        }

        self.client.force_authenticate(user=self.project_manager)

        response = self.client.post(
            self.tasks_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )



    def test_project_manager_cannot_create_task_on_another_project(self):

        data = {
            "title": "Invalid Task",
            "description": "Invalid task",
            "project": self.another_project.id,
            "assigned_to": self.another_team_member.id,
            "priority": "medium",
            "status": "planning",
        }

        self.client.force_authenticate(user=self.project_manager)

        response = self.client.post(
            self.tasks_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )




    def test_organization_admin_can_create_task(self):

        data = {
            "title": "Admin Task",
            "description": "Created by organization admin",
            "project": self.another_project.id,
            "assigned_to": self.another_team_member.id,
            "priority": "high",
            "status": "planning",
        }

        self.client.force_authenticate(user=self.organization_admin)

        response = self.client.post(
            self.tasks_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )


    def test_system_admin_can_create_task(self):

        data = {
            "title": "System Admin Task",
            "description": "Created by system admin",
            "project": self.another_project.id,
            "assigned_to": self.another_team_member.id,
            "priority": "high",
            "status": "planning",
        }

        self.client.force_authenticate(user=self.system_admin)

        response = self.client.post(
            self.tasks_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )


    def test_cannot_assign_task_to_non_team_member(self):

        data = {
            "title": "Invalid Assignment",
            "description": "Invalid assignment",
            "project": self.project.id,
            "assigned_to": self.project_manager.id,
            "priority": "medium",
            "status": "planning",
        }

        self.client.force_authenticate(user=self.project_manager)

        response = self.client.post(
            self.tasks_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )



    def test_cannot_assign_team_member_from_another_project(self):

        data = {
            "title": "Invalid Assignment",
            "description": "Invalid assignment",
            "project": self.project.id,
            "assigned_to": self.another_team_member.id,
            "priority": "medium",
            "status": "planning",
        }

        self.client.force_authenticate(user=self.project_manager)

        response = self.client.post(
            self.tasks_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )



    def test_project_manager_can_update_own_project_task(self):

        data = {
            "title": "Updated Task",
            "description": "Updated description",
            "priority": "high",
        }

        self.client.force_authenticate(user=self.project_manager)

        response = self.client.patch(
            self.task_detail_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    
    def test_project_manager_cannot_update_another_project_task(self):

        data = {
            "title": "Unauthorized Update",
        }

        self.client.force_authenticate(user=self.project_manager)

        response = self.client.patch(
            self.another_task_detail_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )


    def test_organization_admin_can_update_any_task(self):

        data = {
            "title": "Admin Updated Task",
        }

        self.client.force_authenticate(user=self.organization_admin)

        response = self.client.patch(
            self.another_task_detail_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )


    def test_team_member_can_update_task_status(self):

        data = {
            "status": "in_progress",
        }

        self.client.force_authenticate(user=self.team_member)

        response = self.client.patch(
            self.task_detail_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )



    def test_team_member_cannot_update_another_users_task(self):

        data = {
            "status": "in_progress",
        }

        self.client.force_authenticate(user=self.team_member)

        response = self.client.patch(
            self.another_task_detail_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )


    def test_cannot_complete_task_without_completion_details(self):

        data = {
            "status": "completed",
        }

        self.client.force_authenticate(user=self.project_manager)

        response = self.client.patch(
            self.task_detail_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )


    def test_can_complete_task_with_completion_details(self):

        data = {
            "status": "completed",
            "completion_report": "Task completed successfully.",
            "worked_hours": "5.50",
        }

        self.client.force_authenticate(user=self.project_manager)

        response = self.client.patch(
            self.task_detail_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )


    def test_completion_report_requires_completed_status(self):

        data = {
            "completion_report": "Task completed successfully.",
        }

        self.client.force_authenticate(user=self.project_manager)

        response = self.client.patch(
            self.task_detail_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )


    def test_worked_hours_requires_completed_status(self):

        data = {
            "worked_hours": "5.50",
        }

        self.client.force_authenticate(user=self.project_manager)

        response = self.client.patch(
            self.task_detail_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )



    def test_unauthenticated_user_cannot_delete_task(self):

        response = self.client.delete(
            self.task_detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


    def test_team_member_cannot_delete_task(self):

        self.client.force_authenticate(user=self.team_member)

        response = self.client.delete(
            self.task_detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )


    def test_project_manager_can_delete_own_project_task(self):

        self.client.force_authenticate(user=self.project_manager)

        response = self.client.delete(
            self.task_detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

    def test_project_manager_cannot_delete_another_project_task(self):

        self.client.force_authenticate(user=self.project_manager)

        response = self.client.delete(
            self.another_task_detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_organization_admin_can_delete_any_task(self):

        self.client.force_authenticate(user=self.organization_admin)

        response = self.client.delete(
            self.another_task_detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

    def test_system_admin_can_delete_any_task(self):

        self.client.force_authenticate(user=self.system_admin)

        response = self.client.delete(
            self.task_detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )




    def test_project_manager_can_create_unassigned_task(self):

        data = {
            "title": "Unassigned Task",
            "description": "Task without an assigned member",
            "project": self.project.id,
            "priority": "medium",
            "status": "planning",
        }

        self.client.force_authenticate(user=self.project_manager)

        response = self.client.post(
            self.tasks_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    


    

    
    



    


    


    



    



    