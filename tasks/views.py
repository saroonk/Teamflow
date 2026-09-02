from django.shortcuts import render

# Create your views here.

from rest_framework.generics import *
from .permissions import IsTaskAccess
from .serializers import TaskSerializer
from .models import Task
from rest_framework.permissions import AllowAny

from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from django.core.cache import cache

from rest_framework.throttling import ScopedRateThrottle

from comment.cache import invalidate_task_comments_cache
from django.db import transaction
from .tasks import send_task_assignment_email

def invalidate_task_list():
    cache.delete_pattern("teamflow:user:*:tasks:list:*")


def invalidate_task_detail(task_id):
    cache.delete(f"teamflow:task:{task_id}")

class TasksView(ListCreateAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    permission_classes = [IsTaskAccess]
    throttle_classes = [ScopedRateThrottle]

    def get_throttles(self):
        if self.request.method == "GET":
            self.throttle_scope = "task_read"
        elif self.request.method == "POST":
            self.throttle_scope = "task_write"
        return [ScopedRateThrottle()]


    def get_queryset(self):
        user = self.request.user

        if user.role == 'organization_admin' or user.is_superuser:
            return Task.objects.all()
        
        elif user.role == "project_manager":
            return Task.objects.filter(project__in = user.managed_projects.all())
        elif user.role == "team_member":
            return Task.objects.filter(assigned_to = user)

        raise PermissionDenied(
            "You do not have permission to access this project's members."
        )


    def list(self, request, *args, **kwargs):
        queryset =self.get_queryset()

        page = self.paginate_queryset(queryset)

        if page is not None:

            page_number = request.query_params.get("page", "1")

            page_size = request.query_params.get(
                "page_size",
                self.paginator.page_size
            )

            cache_key = (f"teamflow:user:{request.user.id}:"
                        f"tasks:list:page:{page_number}:size:{page_size}")

            cached_data = cache.get(cache_key)

            if cached_data is not None:
                return Response (cached_data)


            serializer = self.get_serializer(
                page,
                many=True
                )

            response = self.get_paginated_response(
                serializer.data
            )

            serialized_data = response.data

            cache.set(
                cache_key,
                serialized_data,
                timeout=300
            )

            return Response(serialized_data)


        serializer =  self.get_serializer(queryset, many=True)

        
        return Response(serializer.data)


    def perform_create(self, serializer):
        user = self.request.user

        task = serializer.save(created_by=user)

        invalidate_task_list()

        if task.assigned_to_id:
            transaction.on_commit(
                lambda task_id=task.id:
                    send_task_assignment_email.delay(task_id)
            )

    




class TasksDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    permission_classes = [IsTaskAccess]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "task_detail"

    def get_queryset(self):
        user = self.request.user

        if user.role == 'organization_admin' or user.is_superuser:
            return Task.objects.all()
        
        elif user.role == "project_manager":
            return Task.objects.filter(project__in = user.managed_projects.all())
        elif user.role == "team_member":
            return Task.objects.filter(assigned_to = user)

        raise PermissionDenied(
            "You do not have permission to access this project's members."
        )

    
    def update(self, request, *args, **kwargs):
        if request.user.role == "team_member":
            kwargs["partial"] = True

        return super().update(request, *args, **kwargs)


    def perform_update(self, serializer):

        old_assignee_id = serializer.instance.assigned_to_id

        instance = serializer.save()

        invalidate_task_list()
        invalidate_task_detail(instance.id)

        new_assignee_id = instance.assigned_to_id

        if new_assignee_id and new_assignee_id != old_assignee_id:
            transaction.on_commit(
                lambda task_id=instance.id:
                    send_task_assignment_email.delay(task_id)
            )

    def perform_destroy(self,instance):
        task_id = instance.id

        instance.delete()

        invalidate_task_list()
        invalidate_task_detail(task_id)
        invalidate_task_comments_cache(task_id)


    
    def retrieve(self, request,*args, **kwargs):
        instance = self.get_object()

        cache_key = f"teamflow:task:{instance.id}"

        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response (cached_data)

        serializer = self.get_serializer(instance)

        serializer_data = serializer.data

        cache.set(cache_key, serializer_data , timeout=300)

        return Response(serializer_data)



        




    



       



      