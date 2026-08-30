
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from .models import Comment

class CommentSerializer(ModelSerializer):
    created_by = serializers.CharField(source="created_by.username", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)
    task_title = serializers.CharField(source="task.title", read_only=True)

    


    def validate(self, attrs):
        request_user = self.context["request"].user

        project = attrs.get("project")
        task = attrs.get("task")

        if task is None and self.instance:
            task = self.instance.task

        if not request_user.is_superuser and request_user.role not in [
                "organization_admin",
                "project_manager",
                "team_member",
            ]:
            raise serializers.ValidationError("You do not have permission to create a comment.")



        
        if request_user.role == "project_manager":
            if task.project not in request_user.managed_projects.all():
                raise serializers.ValidationError(
                    "You can only comment on tasks in your projects."
                )

        # Team member
        elif request_user.role == "team_member":
            if task.assigned_to != request_user:
                raise serializers.ValidationError(
                    "You can only comment on tasks assigned to you."
                )
 

        

        return attrs

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_by', 'project_name', 'task', 'task_title', 'created_at']




class TaskCommentsListSerializer(ModelSerializer):

    created_by = serializers.CharField(source="created_by.username", read_only=True)
    task_title = serializers.CharField(source="task.title", read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_by', 'task', 'task_title', 'created_at']

