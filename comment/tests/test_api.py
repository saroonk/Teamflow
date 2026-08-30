from django.db.models import Q
from rest_framework.test import APITestCase
from rest_framework import status

from accounts.models import User
from organizations.models import Organizations
from projects.models import Project
from tasks.models import Task
from comment.models import Comment


class CommentAPITest(APITestCase):

    def setUp(self):

        self.comments_url = "/api/v1/comments/"

        self.organization = Organizations.objects.create(
            name="Test Organization",
            description="Test description"
        )

        # Users

        self.system_admin = User.objects.create_user(
            username="systemadmin",
            email="systemadmin@example.com",
            password="TestPassword123",
            is_staff=True,
            is_superuser=True,
        )

        self.organization_admin = User.objects.create_user(
            username="organizationadmin",
            email="organizationadmin@example.com",
            password="TestPassword123",
            role="organization_admin",
            organization=self.organization,
        )

        self.project_manager = User.objects.create_user(
            username="projectmanager",
            email="projectmanager@example.com",
            password="TestPassword123",
            role="project_manager",
            organization=self.organization,
        )

        self.another_project_manager = User.objects.create_user(
            username="anothermanager",
            email="anothermanager@example.com",
            password="TestPassword123",
            role="project_manager",
            organization=self.organization,
        )

        self.team_member = User.objects.create_user(
            username="teammember",
            email="teammember@example.com",
            password="TestPassword123",
            role="team_member",
            organization=self.organization,
        )

        self.another_team_member = User.objects.create_user(
            username="anothermember",
            email="anothermember@example.com",
            password="TestPassword123",
            role="team_member",
            organization=self.organization,
        )

        # Projects

        self.project = Project.objects.create(
            title="Project One",
            description="Project One",
            organization=self.organization,
            project_manager=self.project_manager,
            priority="low",
            status="planning",
        )

        self.another_project = Project.objects.create(
            title="Project Two",
            description="Project Two",
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
            description="Task One",
            project=self.project,
            assigned_to=self.team_member,
            created_by=self.project_manager,
            priority="medium",
            status="planning",
        )

        self.another_task = Task.objects.create(
            title="Task Two",
            description="Task Two",
            project=self.another_project,
            assigned_to=self.another_team_member,
            created_by=self.another_project_manager,
            priority="medium",
            status="planning",
        )

        # Comments

        self.comment = Comment.objects.create(
            content="Test comment",
            task=self.task,
            created_by=self.project_manager,
        )

        self.another_comment = Comment.objects.create(
            content="Another comment",
            task=self.another_task,
            created_by=self.another_project_manager,
        )


    def test_unauthenticated_user_cannot_view_comments(self):

        response = self.client.get(self.comments_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


    def test_system_admin_can_view_task_comments(self):

        url = f"/api/v1/tasks/{self.task.id}/comments/"

        self.client.force_authenticate(user=self.system_admin)

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )


    def test_project_manager_can_view_own_project_comments(self):

        url = f"/api/v1/tasks/{self.task.id}/comments/"

        self.client.force_authenticate(user=self.project_manager)

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )


    def test_project_manager_cannot_view_other_project_comments(self):

        url = f"/api/v1/tasks/{self.another_task.id}/comments/"

        self.client.force_authenticate(user=self.project_manager)

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            0
        )

    def test_team_member_can_view_assigned_task_comments(self):

        url = f"/api/v1/tasks/{self.task.id}/comments/"

        self.client.force_authenticate(user=self.team_member)

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

    def test_team_member_cannot_view_other_member_task_comments(self):

        url = f"/api/v1/tasks/{self.another_task.id}/comments/"

        self.client.force_authenticate(user=self.team_member)

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            0
        )


    def test_team_member_can_view_comment_created_by_them(self):

        comment = Comment.objects.create(
            content="My own comment",
            task=self.another_task,
            created_by=self.team_member,
        )

        self.client.force_authenticate(user=self.team_member)

        response = self.client.get(
            self.comments_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        comment_ids = [item["id"] for item in response.data]

        self.assertIn(comment.id, comment_ids)



    def test_system_admin_can_create_comment(self):

        data = {
            "content": "System admin comment",
            "task": self.another_task.id,
        }

        self.client.force_authenticate(user=self.system_admin)

        response = self.client.post(
            self.comments_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )


    def test_organization_admin_can_create_comment(self):

        data = {
            "content": "Organization admin comment",
            "task": self.task.id,
        }

        self.client.force_authenticate(user=self.organization_admin)

        response = self.client.post(
            self.comments_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )




    def test_project_manager_can_create_comment_on_own_project(self):

        data = {
            "content": "Project manager comment",
            "task": self.task.id,
        }

        self.client.force_authenticate(user=self.project_manager)

        response = self.client.post(
            self.comments_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )


    def test_project_manager_cannot_comment_on_other_project(self):

        data = {
            "content": "Unauthorized comment",
            "task": self.another_task.id,
        }

        self.client.force_authenticate(user=self.project_manager)

        response = self.client.post(
            self.comments_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )


    def test_team_member_can_comment_on_assigned_task(self):

        data = {
            "content": "Team member comment",
            "task": self.task.id,
        }

        self.client.force_authenticate(user=self.team_member)

        response = self.client.post(
            self.comments_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )




    def test_team_member_cannot_comment_on_other_member_task(self):

        data = {
            "content": "Unauthorized comment",
            "task": self.another_task.id,
        }

        self.client.force_authenticate(user=self.team_member)

        response = self.client.post(
            self.comments_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )



    def test_created_by_is_authenticated_user(self):

        data = {
            "content": "My comment",
            "task": self.task.id,
        }

        self.client.force_authenticate(user=self.team_member)

        response = self.client.post(
            self.comments_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.data["created_by"],
            self.team_member.username
        )



    def test_comment_author_can_update_comment(self):

        url = f"{self.comments_url}{self.comment.id}/"

        data = {
            "content": "Updated comment"
        }

        self.client.force_authenticate(user=self.project_manager)

        response = self.client.patch(
            url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )


    def test_comment_can_be_patched_without_task(self):

        url = f"{self.comments_url}{self.comment.id}/"

        data = {
            "content": "Only content changed"
        }

        self.client.force_authenticate(user=self.project_manager)

        response = self.client.patch(
            url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.comment.refresh_from_db()

        self.assertEqual(
            self.comment.content,
            "Only content changed"
        )




    def test_team_member_cannot_update_other_users_comment(self):

        url = f"{self.comments_url}{self.comment.id}/"

        data = {
            "content": "Unauthorized edit"
        }

        self.client.force_authenticate(user=self.team_member)

        response = self.client.patch(
            url,
            data,
            format="json"
        )

    

    def test_comment_author_can_delete_comment(self):

        url = f"{self.comments_url}{self.comment.id}/"

        self.client.force_authenticate(user=self.project_manager)

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )



    def test_system_admin_can_delete_any_comment(self):

        url = f"{self.comments_url}{self.another_comment.id}/"

        self.client.force_authenticate(user=self.system_admin)

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )