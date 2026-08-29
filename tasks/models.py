from django.db import models

# Create your models here.

from projects.models import Project
from accounts.models import User




class Task(models.Model):
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
    description = models.TextField()
    project = models.ForeignKey(Project , on_delete=models.CASCADE, related_name="tasks")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL , blank=True ,null=True ,related_name="assigned_tasks")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT , related_name="created_tasks")
    completion_report = models.TextField(blank=True,null=True)
    worked_hours = models.DecimalField(blank=True,null=True ,decimal_places=2,max_digits=5)

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
    due_date =  models.DateTimeField(blank=True,null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    
        



    


