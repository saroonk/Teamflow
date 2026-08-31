from django.shortcuts import render

# Create your views here.

from .serializer import *

from .permissions import *

from rest_framework.generics import *

from .models import *

from rest_framework.permissions import *

from rest_framework.response import Response
from rest_framework import status

from .permissions import IsProjectCreatorAdmin,IsTeamMemberViewer

from django.core.cache import cache


from django.shortcuts import get_object_or_404

from rest_framework.exceptions import PermissionDenied

from .cache import invalidate_project_members_cache

from rest_framework.throttling import ScopedRateThrottle

def invalidate_project_list_cache():
    cache.delete_pattern("teamflow:user:*:projects:list")

def invalidate_project_detail_cache(project_id):
    cache.delete(f"teamflow:project:{project_id}")

# def invalidate_project_members_cache(project_id):
#     cache.delete(f"teamflow:project:{project_id}:members:list")


class ProjectsView(ListCreateAPIView):
    serializer_class = ProjectSerializer
    queryset =  Project.objects.all() 
    permission_classes = [IsProjectCreatorAdmin]
    throttle_classes = [ScopedRateThrottle]

    def get_throttles(self):
        if self.request.method == "GET":
            self.throttle_scope = "projects_read"
        elif self.request.method == "POST":
            self.throttle_scope = "projects_write"
        return [ScopedRateThrottle()]



    def list(self, request, *args, **kwargs):
        cache_key = f"teamflow:user:{request.user.id}:projects:list"

        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)

        serialized_data = serializer.data

        cache.set(
            cache_key,
            serialized_data,
            timeout=300
        )

        return Response(serialized_data)

    def perform_create(self,serializer):
        if self.request.user.role == "project_manager":

            serializer.save(
                project_manager = self.request.user , 
                organization = self.request.user.organization
                )
        else:
            serializer.save()

        invalidate_project_list_cache()

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.role == "organization_admin":
            return Project.objects.all()

        if user.role == "project_manager":
            return user.managed_projects.all()

        if user.role == "team_member":
            return user.projects.all()

        raise PermissionDenied(
            "You do not have permission to access projects."
        )



    
class ProjectsDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    queryset =  Project.objects.all() 
    permission_classes = [IsProjectCreatorAdmin]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "projects_detail"

    def get_queryset(self):
        user = self.request.user
        if user.role == "organization_admin" or user.is_superuser:
                return Project.objects.all()
        elif user.role == "project_manager":
            return user.managed_projects.all()
        elif user.role == "team_member":
            return user.projects.all()
        raise PermissionDenied(
                "You do not have permission to access this project."
            )


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        cache_key = f"teamflow:project:{instance.id}"

        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)


        serializer = self.get_serializer(instance)

        serialized_data = serializer.data

        cache.set(
            cache_key,
            serialized_data,
            timeout=300
        )

        return Response(serialized_data)



    def perform_update(self, serializer):
        instance = serializer.save()

        invalidate_project_list_cache()
        invalidate_project_detail_cache(instance.id)

        if "team_members" in serializer.validated_data:
            invalidate_project_members_cache(instance.id)



    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        project_id = instance.id

        instance.delete()

        invalidate_project_list_cache()
        invalidate_project_detail_cache(project_id)
        invalidate_project_members_cache(project_id)

        return Response(
            {"message": "Project deleted successfully."},
            status=status.HTTP_200_OK
        )






class ProjectMembersView(ListAPIView):
    serializer_class = ProjectMemberSerializer
    queryset = User.objects.all()
    permission_classes = [IsTeamMemberViewer]

    def get_queryset(self):
        project_id = self.kwargs['pk']
        project = get_object_or_404(Project, pk=project_id)
        user = self.request.user

        if user.is_superuser or user.role == "organization_admin":
            return project.team_members.all()

        if user.role == "project_manager":
            if project.project_manager == user:
                return project.team_members.all()

        raise PermissionDenied(
            "You do not have permission to access this project's members."
        )


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        project_id = self.kwargs['pk']
        cache_key = f"teamflow:project:{project_id}:members:list"

        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        serializer = self.get_serializer(queryset, many=True)

        serialized_data = serializer.data

        cache.set(
            cache_key,
            serialized_data,
            timeout=300
        )

        return Response(serialized_data)
        
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['project'] = get_object_or_404(
            Project,
            pk=self.kwargs['pk']
        )
        return context

