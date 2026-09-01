from django.core.cache import cache
from rest_framework.test import APITestCase

from accounts.models import User
from organizations.models import Organizations
from projects.models import Project
from tasks.models import Task

from comment.models import Comment


class CommentCachingTests(APITestCase):

    def setUp(self):
        cache.clear()

        self.organization = Organizations.objects.create(
            name="Test Organization",
            description="Test description"
        )

        self.system_admin = User.objects.create_user(
            username="testsystemadmin",
            email="testsystemadmin@example.com",
            password="TestPassword123",
            is_staff=True,
            is_superuser=True
        )

        self.project_manager = User.objects.create_user(
            username="testprojectmanager",
            email="testprojectmanager@example.com",
            password="TestPassword123",
            role="project_manager",
            organization=self.organization
        )

        self.team_member = User.objects.create_user(
            username="testteammember",
            email="testteammember@example.com",
            password="TestPassword123",
            role="team_member",
            organization=self.organization
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

        self.task = Task.objects.create(
            title="Test Task",
            description="Test task description",
            project=self.project,
            assigned_to=self.team_member,
            created_by=self.project_manager
        )

        self.comment = Comment.objects.create(
            task=self.task,
            created_by=self.team_member,
            content="Initial comment"
        )


    def test_task_comments_cache_is_created(self):

        self.client.force_authenticate(
            user=self.system_admin
        )

        response = self.client.get(
            f"/api/v1/tasks/{self.task.id}/comments/"
        )

        self.assertEqual(response.status_code, 200)



        cache_key = (
            f"teamflow:user:{self.system_admin.id}:"
            f"task:{self.task.id}:comments:list:"
            f"page:1:size:10"
        )

        cached_data = cache.get(cache_key)

        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data, response.data)


    def test_create_comment_invalidates_cache(self):

        self.client.force_authenticate(
            user=self.system_admin
        )

        response = self.client.get(
            f"/api/v1/tasks/{self.task.id}/comments/"
        )

        self.assertEqual(response.status_code, 200)

        cache_key = (
            f"teamflow:user:{self.system_admin.id}:"
            f"task:{self.task.id}:comments:list:"
            f"page:1:size:10"
        )

        self.assertIsNotNone(cache.get(cache_key))

        response = self.client.post(
            "/api/v1/comments/",
            {
                "task": self.task.id,
                "content": "New comment"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)

        self.assertIsNone(cache.get(cache_key))


    def test_update_comment_invalidates_cache(self):

        self.client.force_authenticate(
            user=self.system_admin
        )

        response = self.client.get(
            f"/api/v1/tasks/{self.task.id}/comments/"
        )

        self.assertEqual(response.status_code, 200)

        cache_key = (
            f"teamflow:user:{self.system_admin.id}:"
            f"task:{self.task.id}:comments:list:"
            f"page:1:size:10"
        )

        self.assertIsNotNone(cache.get(cache_key))

        response = self.client.patch(
            f"/api/v1/comments/{self.comment.id}/",
            {
                "content": "Updated comment"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        self.assertIsNone(cache.get(cache_key))


    def test_delete_comment_invalidates_cache(self):

        self.client.force_authenticate(
            user=self.system_admin
        )

        response = self.client.get(
            f"/api/v1/tasks/{self.task.id}/comments/"
        )

        self.assertEqual(response.status_code, 200)

        cache_key = (
            f"teamflow:user:{self.system_admin.id}:"
            f"task:{self.task.id}:comments:list:"
            f"page:1:size:10"
        )

        self.assertIsNotNone(cache.get(cache_key))

        response = self.client.delete(
            f"/api/v1/comments/{self.comment.id}/"
        )

        self.assertEqual(response.status_code, 204)

        self.assertIsNone(cache.get(cache_key))