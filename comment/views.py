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


    def perform_create(self,serializer):
        user = self.request.user
        return serializer.save(created_by = user)





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
