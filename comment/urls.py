from django.urls import path
from .views import *

urlpatterns = [
    
    path("comments/" , CommentView.as_view() , name="comments"),
    path("comments/<int:pk>/" , CommentDetailView.as_view() , name="commentsdetail"),

    path("tasks/<int:pk>/comments/" , TaskCommentsList.as_view() , name="taskcommentslist"),


    # path("projects/<int:pk>/" , ProjectsDetailView.as_view() , name="projects-detail"),

    # path("projects/<int:pk>/members/" , ProjectMembersView.as_view() , name="project-members")

    # /api/v1/tasks/1/comments/
    #
]