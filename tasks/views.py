from django.shortcuts import render

# Create your views here.

from rest_framework.generics import *
from .permissions import IsTaskAccess
from .serializers import TaskSerializer
from .models import Task
from rest_framework.permissions import AllowAny

from rest_framework.response import Response


from django.core.cache import cache



def invalidate_task_list():
    cache.delete_pattern("teamflow:user:*:tasks:list")


def invalidate_task_detail(task_id):
    cache.delete(f"teamflow:task:{task_id}")

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

    def list(self, request, *args, **kwargs):
        cache_key = f"teamflow:user:{request.user.id}:tasks:list"

        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response (cached_data)

        queryset =self.get_queryset()

        serializer =  self.serializer_class(queryset, many=True)

        serializer_data = serializer.data

        cache.set(cache_key,serializer_data,timeout=300)

        return Response(serializer_data)


    def perform_create(self, serializer):
        user = self.request.user

        serializer.save(created_by=user)

        invalidate_task_list()

    




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
            kwargs["partial"] = True

        return super().update(request, *args, **kwargs)


    def perform_update(self, serializer):
        instance = serializer.save()

        invalidate_task_list()
        invalidate_task_detail(instance.id)

    def perform_destroy(self,instance):
        task_id = instance.id

        instance.delete()

        invalidate_task_list()
        invalidate_task_detail(task_id)


    
    def retrieve(self, request,*args, **kwargs):
        instance = self.get_object()

        cache_key = f"teamflow:task:{instance.id}"

        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response (cached_data)

        serializer = self.serializer_class(instance)

        serializer_data = serializer.data

        cache.set(cache_key, serializer_data , timeout=300)

        return Response(serializer_data)



        




    



       



      