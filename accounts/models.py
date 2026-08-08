from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ("organization_admin", "Organization Admin"),
        ("project_manager", "Project Manager"),
        ("team_member", "Team Member"),
    )


    organization = models.ForeignKey(
        "organizations.Organizations",
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
        )

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']