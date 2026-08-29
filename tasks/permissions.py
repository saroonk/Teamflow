
from rest_framework.permissions import BasePermission   



class IsTaskAccess(BasePermission):

    def has_permission(self, request, view):

        if request.method == "GET" or request.method == "PUT" or request.method == "PATCH":
            return request.user.is_authenticated and (request.user.is_superuser or request.user.role in [
                "project_manager",
                "organization_admin",
                "team_member",
            ])

        if request.method == "POST" or request.method == "DELETE" :
            return request.user.is_authenticated and (request.user.is_superuser or  request.user.role in [
                "project_manager",
                "organization_admin",
            ])

        return False