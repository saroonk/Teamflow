from django.db import models

# Create your models here.


class Comment(models.Model):
    content = models.TextField()
    created_by = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="comments"
    )
    task = models.ForeignKey(
        "tasks.Task", on_delete=models.CASCADE, related_name="comments"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.created_by.username} on - {self.task.title}"