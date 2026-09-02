from django.core.cache import cache
from rest_framework.test import APITestCase
from django.test import override_settings

from accounts.models import User
from organizations.models import Organizations
from projects.models import Project
from tasks.models import Task


class TaskCachingThrottlingTests(APITestCase):

    def setUp(self):
        cache.clear()

        self.organization = Organizations.objects.create(
            name="Test Organization",
            description="Test description"
        )

        self.system_admin = User.objects.create_user(
            username="testadmin",
            email="testadmin@example.com",
            password="TestPassword123",
            is_staff=True,
            is_superuser=True
        )

        self.project_manager = User.objects.create_user(
            username="testpm",
            email="testpm@example.com",
            password="TestPassword123",
            role="project_manager",
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

        self.task = Task.objects.create(
            title="Test Task",
            description="Test task description",
            project=self.project,
            created_by=self.system_admin
        )

    
    def test_task_list_cache_is_created(self):
        self.client.force_authenticate(user=self.system_admin)

        response = self.client.get("/api/v1/tasks/")

        self.assertEqual(response.status_code, 200)

        cache_key = (
            f"teamflow:user:{self.system_admin.id}:tasks:list:"
            f"status::"
            f"priority::page:1:size:10"
        )

        cached_data = cache.get(cache_key)

        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data, response.data)

    def test_task_list_cache_is_invalidated_after_create(self):
        self.client.force_authenticate(user=self.system_admin)

        # First request creates cache
        response = self.client.get("/api/v1/tasks/")

        self.assertEqual(response.status_code, 200)

        cache_key = (
            f"teamflow:user:{self.system_admin.id}:tasks:list:"
            f"status::"
            f"priority::page:1:size:10"
        )

        self.assertIsNotNone(cache.get(cache_key))

        # Create task
        response = self.client.post(
            "/api/v1/tasks/",
            {
                "title": "New Task",
                "description": "New task description",
                "project": self.project.id,
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)

        # Cache should be removed
        self.assertIsNone(cache.get(cache_key))

    def test_task_detail_cache_is_created(self):
        self.client.force_authenticate(user=self.system_admin)

        response = self.client.get(
            f"/api/v1/tasks/{self.task.id}/"
        )

        self.assertEqual(response.status_code, 200)

        cache_key = f"teamflow:task:{self.task.id}"

        cached_data = cache.get(cache_key)

        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data, response.data)

    def test_task_detail_cache_is_invalidated_after_update(self):
        self.client.force_authenticate(user=self.system_admin)

        # Create detail cache
        response = self.client.get(
            f"/api/v1/tasks/{self.task.id}/"
        )

        self.assertEqual(response.status_code, 200)

        cache_key = f"teamflow:task:{self.task.id}"

        self.assertIsNotNone(cache.get(cache_key))

        # Update task
        response = self.client.patch(
            f"/api/v1/tasks/{self.task.id}/",
            {
                "title": "Updated Task"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        # Cache should be deleted
        self.assertIsNone(cache.get(cache_key))

    def test_task_detail_cache_is_invalidated_after_delete(self):
        self.client.force_authenticate(user=self.system_admin)

        response = self.client.get(
            f"/api/v1/tasks/{self.task.id}/"
        )

        self.assertEqual(response.status_code, 200)

        cache_key = f"teamflow:task:{self.task.id}"

        self.assertIsNotNone(cache.get(cache_key))

        response = self.client.delete(
            f"/api/v1/tasks/{self.task.id}/"
        )

        self.assertEqual(response.status_code, 204)

        self.assertIsNone(cache.get(cache_key))


