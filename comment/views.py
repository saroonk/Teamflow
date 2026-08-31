from django.shortcuts import render
from rest_framework.generics import *
from .serializers import CommentSerializer,TaskCommentsListSerializer
from .models import Comment
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response

from rest_framework import status
from rest_framework.views import APIView
# Create your views here.


from .permissions import IsCommentModificationAllowed

from django.db.models import Q
from django.core.cache import cache


def invalidate_task_comments_cache(task_id):
    cache.delete_pattern(
        f"teamflow:user:*:task:{task_id}:comments:list"
    )

class CommentView(ListCreateAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'organization_admin' or user.is_superuser:
            return Comment.objects.all()
        
        elif user.role == "project_manager":
            return Comment.objects.filter(task__project__in = user.managed_projects.all())
        elif user.role == "team_member":
            return Comment.objects.filter(Q(task__assigned_to = user)|Q(created_by = user))
        return Comment.objects.none()


   
    
    def perform_create(self, serializer):
        user = self.request.user

        comment = serializer.save(created_by=user)

        invalidate_task_comments_cache(
            comment.task_id
        )





class CommentDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = [
        IsAuthenticated,
        IsCommentModificationAllowed,
    ]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'organization_admin' or user.is_superuser:
            return Comment.objects.all()
        
        elif user.role == "project_manager":
            return Comment.objects.filter(task__project__in = user.managed_projects.all())
        elif user.role == "team_member":
            return Comment.objects.filter(Q(task__assigned_to = user)|Q(created_by = user))
        return Comment.objects.none()


    def perform_update(self, serializer):
        instance = serializer.save()

        invalidate_task_comments_cache(
            instance.task_id
        )

    def perform_destroy(self, instance):
        task_id = instance.task_id

        instance.delete()

        invalidate_task_comments_cache(task_id)




class TaskCommentsList(ListAPIView):

    serializer_class = TaskCommentsListSerializer

    permission_classes = [IsAuthenticated]




    def get_queryset(self):
        user = self.request.user

        task_id = self.kwargs['pk']


        if user.role == 'organization_admin' or user.is_superuser:
            return Comment.objects.filter(task__id = task_id)
        
        elif user.role == "project_manager":
            return Comment.objects.filter(task__project__in = user.managed_projects.all() , task__id = task_id)

        elif user.role == "team_member":
            return Comment.objects.filter(task_id=task_id).filter(Q(task__assigned_to=user) |Q(created_by=user))
        return Comment.objects.none()



    def list(self, request, *args, **kwargs):
        task_id = self.kwargs["pk"]

        cache_key = (
            f"teamflow:user:{request.user.id}:"
            f"task:{task_id}:comments:list"
        )

        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        queryset = self.get_queryset()

        serializer = self.get_serializer(
            queryset,
            many=True
        )

        serialized_data = serializer.data

        cache.set(
            cache_key,
            serialized_data,
            timeout=300
        )

        return Response(serialized_data)
