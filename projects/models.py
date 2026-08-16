from django.db import models
from accounts.models import User
from organizations.models import Organizations


class Project(models.Model):

    PRIORITY_CHOICES = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    )

    STATUS_CHOICES = (
        ("planning", "Planning"),
        ("in_progress", "In Progress"),
        ("on_hold", "On Hold"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    organization = models.ForeignKey(
        Organizations,
        on_delete=models.CASCADE,
        related_name="projects",
    )

    project_manager = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="managed_projects",
    )

    team_members = models.ManyToManyField(
        User,
        related_name="projects",
        blank=True,
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="medium",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planning",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title