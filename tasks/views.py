from django.shortcuts import render

# Create your views here.

from rest_framework.generics import *
from .permissions import IsTaskAccess
from .serializers import TaskSerializer
from .models import Task
from rest_framework.permissions import AllowAny

class TasksView(ListCreateAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    permission_classes = [IsTaskAccess]


    def get_queryset(self):
        user = self.request.user

        if user.role == 'organization_admin' or user.is_superuser:
            return Task.objects.all()
        
        elif user.role == "project_manager":
            return Task.objects.filter(project__in = user.managed_projects.all())
        elif user.role == "team_member":
            return Task.objects.filter(assigned_to = user)
        return Task.objects.none()


    def perform_create(self,serializer):
        user = self.request.user
        return serializer.save(created_by = user)
    




class TasksDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    permission_classes = [IsTaskAccess]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'organization_admin' or user.is_superuser:
            return Task.objects.all()
        
        elif user.role == "project_manager":
            return Task.objects.filter(project__in = user.managed_projects.all())
        elif user.role == "team_member":
            return Task.objects.filter(assigned_to = user)
        return Task.objects.none()
    
    def update(self, request, *args, **kwargs):
        if request.user.role == "team_member":
            kwargs['partial'] = True

        return super().update(request, *args, **kwargs)

    



       




# ("organization_admin", "Organization Admin"),
#         ("project_manager", "Project Manager"),
#         ("team_member", "Team Member"),       