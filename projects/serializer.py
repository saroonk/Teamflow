from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import *

class ProjectSerializer(ModelSerializer):

    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organizations.objects.all(),
        write_only=True,
        required=False
    )

    project_manager = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        required=False
    )

    team_members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        required=False
    )

    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True
    )

    manager = serializers.SerializerMethodField()

    team_members_name = serializers.SerializerMethodField()

    def validate(self, attrs):
        request_user = self.context["request"].user

        if request_user.role != "project_manager":
            if "organization" not in attrs:
                raise serializers.ValidationError({
                    "organization": "This field is required."
                })

            if "project_manager" not in attrs:
                raise serializers.ValidationError({
                    "project_manager": "This field is required."
                })

        if request_user.role == "project_manager":
            if "project_manager" in attrs or "organization" in attrs:
                raise serializers.ValidationError("You cant update those values")


        return attrs

    def validate_project_manager(self, value):
        if value.role == "project_manager":
            return value

        raise serializers.ValidationError(
            "The user is not a project manager"
        )

    def validate_team_members(self, value):
        for user in value:
            if user.role != "team_member":
                raise serializers.ValidationError(
                    f"{user.username} is not a team member"
                )

        return value

    def get_manager(self, obj):
        return obj.project_manager.username

    def get_team_members_name(self, obj):
        return [user.username for user in obj.team_members.all()]

    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "organization",
            "project_manager",
            "team_members",
            "organization_name",
            "manager",
            "team_members_name",
            "priority",
            "status",
        ]