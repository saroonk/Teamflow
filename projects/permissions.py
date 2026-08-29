
from rest_framework.permissions import BasePermission   



class IsProjectCreatorAdmin(BasePermission):

    def has_permission(self, request, view):

        if request.method == "GET":
            return request.user.is_authenticated and (request.user.is_superuser or request.user.role in [
                "project_manager",
                "organization_admin",
                "team_member",
            ])

        if request.method == "POST" or request.method == "PUT" or request.method == "PATCH":
            return request.user.is_authenticated and (request.user.is_superuser or  request.user.role in [
                "project_manager",
                "organization_admin",
            ])


        if request.method == "DELETE":
            return request.user.is_authenticated and (request.user.is_superuser or  request.user.role == "organization_admin")

               

        

        

        return False




class IsTeamMemberViewer(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_superuser or request.user.role in [
                "project_manager",
                "organization_admin",
                
            ])

