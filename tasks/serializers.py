from rest_framework.serializers import ModelSerializer
from .models import Task

from rest_framework import serializers
from rest_framework.validators import ValidationError

from projects.models import Project
from accounts.models import User


class TaskSerializer(ModelSerializer):

    created_by = serializers.CharField(read_only=True)

    project_name = serializers.CharField(source="project.title", read_only=True)

    assigned_members =  serializers.SerializerMethodField()

    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        write_only=True
    )

    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )


    def get_assigned_members(self, obj):
        return obj.assigned_to.username if obj.assigned_to else None
    class Meta:
        model = Task
        fields = ['id','title','description','assigned_members','project_name','project','assigned_to','created_by','completion_report','worked_hours','priority','status','due_date','created_at','updated_at']

    def validate(self,attrs):

        user = self.context['request'].user

        if user.role == "team_member":
            allowed_fields = {
                'status',
                'completion_report',
                'worked_hours'
            }

            invalid_fields = set(attrs.keys()) - allowed_fields

            if invalid_fields:
                raise ValidationError({
                    'detail': (
                        'Team members can only update '
                        'status, completion report and worked hours.'
                    )
                })

        project = attrs.get('project')
        created = attrs.get('created_by')
        assigned = attrs.get('assigned_to')
        completion = attrs.get('completion_report')
        worked = attrs.get('worked_hours')
        status = attrs.get('status')


        if user.role == "project_manager" and not self.instance:
            if project not in user.managed_projects.all():
                raise ValidationError(
                    "You can't create a task on another project."
                )
        

        if project and assigned and assigned.role == "team_member":
            if not project in assigned.projects.all():
                raise ValidationError("You cant assign task to team member of other projects")
        
        if assigned and not assigned.role == "team_member":
            raise ValidationError("You can only assign task to team members")

        
        
        if status == "completed" and (not completion or not worked):
            raise ValidationError("You must provide completion report and worked hours when marking task as completed")
        
        
        if (completion or worked) and not status == "completed":
            raise ValidationError("You must mark task as completed when providing completion report")

        return attrs
        


        
        
