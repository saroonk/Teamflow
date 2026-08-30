from rest_framework.permissions import BasePermission


class IsCommentModificationAllowed(BasePermission):

    def has_object_permission(self, request, view, obj):

        user = request.user

        if user.is_superuser:
            return True

        if user.role == "organization_admin":
            return True

        if user.role == "project_manager":
            return obj.task.project in user.managed_projects.all()

        if user.role == "team_member":
            return obj.created_by == user

        return False