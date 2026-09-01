from django.core.cache import cache
from rest_framework.test import APITestCase
from accounts.models import User

from organizations.models import Organizations
from projects.models import Project



class ProjectCachingTests(APITestCase):

    def setUp(self):
        cache.clear()

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

        self.project = Project.objects.create(
            title="Test Project",
            description="Test description",
            organization=self.organization,
            project_manager=self.project_manager,
            priority="low",
            status="planning"
        )


    def test_project_list_cache_is_created(self):

        self.client.force_authenticate(user=self.system_admin)

        response = self.client.get("/api/v1/projects/")

        self.assertEqual(response.status_code, 200)

        cache_key = (
            f"teamflow:user:{self.system_admin.id}:projects:list:"
            f"page:1:size:10"
        )

        cached_data = cache.get(cache_key)

        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data, response.data)

    
    def test_project_detail_cache_is_created(self):
        self.client.force_authenticate(user=self.system_admin)

        response = self.client.get(
            f"/api/v1/projects/{self.project.id}/"
        )

        self.assertEqual(response.status_code, 200)

        cache_key = f"teamflow:project:{self.project.id}"

        cached_data = cache.get(cache_key)

        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data, response.data)



    def test_project_members_cache_is_created(self):
        self.client.force_authenticate(user=self.system_admin)

        response = self.client.get(
            f"/api/v1/projects/{self.project.id}/members/"
        )

        self.assertEqual(response.status_code, 200)

        cache_key = (
            f"teamflow:project:{self.project.id}:members:list"
        )

        cached_data = cache.get(cache_key)

        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data, response.data)


    def test_project_update_invalidates_cache(self):
        self.client.force_authenticate(user=self.system_admin)

        response = self.client.get(
            f"/api/v1/projects/{self.project.id}/"
        )

        self.assertEqual(response.status_code, 200)

        cache_key = f"teamflow:project:{self.project.id}"

        self.assertIsNotNone(cache.get(cache_key))

        response = self.client.patch(
            f"/api/v1/projects/{self.project.id}/",
            {
                "title": "Updated Project"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        self.assertIsNone(cache.get(cache_key))

    def test_project_list_cache_is_created(self):
        self.client.force_authenticate(user=self.system_admin)

        response = self.client.get("/api/v1/projects/")

        self.assertEqual(response.status_code, 200)

        cache_key = (
            f"teamflow:user:{self.system_admin.id}:projects:list:"
            f"page:1:size:10"
        )


        cached_data = cache.get(cache_key)

        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data, response.data)

    def test_project_list_cache_is_invalidated_after_create(self):
        self.client.force_authenticate(user=self.system_admin)

        response = self.client.get("/api/v1/projects/")
        self.assertEqual(response.status_code, 200)

        cache_key = (
            f"teamflow:user:{self.system_admin.id}:projects:list:"
            f"page:1:size:10"
        )

        self.assertIsNotNone(cache.get(cache_key))

        response = self.client.post(
            "/api/v1/projects/",
            {
                "title": "New Project",
                "description": "New project description",
                "organization": self.organization.id,
                "project_manager": self.project_manager.id,
                "priority": "low",
                "status": "planning"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)

        self.assertIsNone(cache.get(cache_key))


    def test_project_detail_cache_is_invalidated_after_delete(self):
        self.client.force_authenticate(user=self.system_admin)

        response = self.client.get(
            f"/api/v1/projects/{self.project.id}/"
        )

        self.assertEqual(response.status_code, 200)

        cache_key = f"teamflow:project:{self.project.id}"

        self.assertIsNotNone(cache.get(cache_key))

        response = self.client.delete(
            f"/api/v1/projects/{self.project.id}/"
        )

        self.assertEqual(response.status_code, 200)

        self.assertIsNone(cache.get(cache_key))

    def test_project_members_cache_is_invalidated_after_member_update(self):
        self.client.force_authenticate(user=self.system_admin)

        self.project.team_members.add(self.team_member)

        response = self.client.get(
            f"/api/v1/projects/{self.project.id}/members/"
        )

        self.assertEqual(response.status_code, 200)

        cache_key = (
            f"teamflow:project:{self.project.id}:members:list"
        )

        self.assertIsNotNone(cache.get(cache_key))

        response = self.client.patch(
            f"/api/v1/projects/{self.project.id}/",
            {
                "team_members": []
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        self.assertIsNone(cache.get(cache_key))