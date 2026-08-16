from django.shortcuts import render

# Create your views here.

from .serializer import *

from .permissions import *

from rest_framework.generics import *

from .models import *

from rest_framework.permissions import *

from rest_framework.response import Response
from rest_framework import status

from .permissions import IsProjectCreatorAdmin

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


