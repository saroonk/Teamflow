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

class ProjectsView(ListCreateAPIView):
    serializer_class = ProjectSerializer
    queryset =  Project.objects.all() 
    permission_classes = [IsProjectCreatorAdmin]




    def perform_create(self,serializer):
        if self.request.user.role == "project_manager":

            serializer.save(
                project_manager = self.request.user , 
                organization = self.request.user.organization
                )
        else:
            serializer.save()

    def get_queryset(self):
        user = self.request.user
        if user.role == "project_manager":
            return user.managed_projects.all()
        elif user.role == "team_member":
            return user.projects.all()
        else:
            return Project.objects.all()



    
class ProjectsDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    queryset =  Project.objects.all() 
    permission_classes = [IsProjectCreatorAdmin]

    def get_queryset(self):
        user = self.request.user

        if user.role == "organization_admin" or user.is_superuser:
                return Project.objects.all()
        elif user.role == "project_manager":
            return user.managed_projects.all()
        elif user.role == "team_member":
            return user.projects.all()


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        instance.delete()
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
        project = Project.objects.get(pk = project_id)
        user =self.request.user

        if user.is_superuser or user.role == "organization_admin":
            return project.team_members.all()
        
        if user.role == "project_manager":
            if project.project_manager == user  :
                return project.team_members.all()
        
        return User.objects.none()
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['project'] = get_object_or_404(
            Project,
            pk=self.kwargs['pk']
        )
        return context

