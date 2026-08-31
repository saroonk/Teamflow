from django.core.cache import cache
from rest_framework.test import APITestCase

from accounts.models import User
from organizations.models import Organizations
from projects.models import Project


class UserProjectMembersCacheTests(APITestCase):

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
            username="testmanager",
            email="testmanager@example.com",
            password="TestPassword123",
            role="project_manager",
            organization=self.organization
        )

        self.team_member = User.objects.create_user(
            username="testmember",
            email="testmember@example.com",
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

    def test_user_update_invalidates_project_members_cache(self):

        self.client.force_authenticate(
            user=self.system_admin
        )

        response = self.client.get(
            f"/api/v1/projects/{self.project.id}/members/"
        )

        self.assertEqual(response.status_code, 200)

        cache_key = (
            f"teamflow:project:{self.project.id}:members:list"
        )

        self.assertIsNotNone(
            cache.get(cache_key)
        )

        response = self.client.patch(
            f"/api/v1/auth/users/{self.team_member.id}/",
            {
                "username": "updatedmember"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        self.assertIsNone(
            cache.get(cache_key)
        )