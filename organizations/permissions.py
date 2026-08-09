from rest_framework.permissions import BasePermission


class IsOrganizationManager(BasePermission):

    def has_permission(self,request,view):

        if not request.user.is_authenticated:
            return False

        
        if request.method in ['GET']:
            return (request.user.is_superuser or request.user.role == "organization_admin")

        return request.user.is_superuser