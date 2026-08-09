from rest_framework.permissions import BasePermission



class IsSystemAdmin(BasePermission):

    def has_permission(self,request, view):
        return (request.user.is_authenticated and request.user.is_superuser)


class IsOrganizationAdmin(BasePermission):
    def has_permission(self,request ,view):
        return (request.user.role == 'organization_admin' and request.user.is_authenticated)


class IsProjectManager(BasePermission):
    def has_permission(self,request ,view):
        return (request.user.role == 'project_manager' and request.user.is_authenticated)

class IsTeamMember(BasePermission):
    def has_permission(self,request ,view):
        return (request.user.role == 'team_member' and request.user.is_authenticated)



class IsSystemOrOrganizationAdmin(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.role == "organization_admin"
            )
        )