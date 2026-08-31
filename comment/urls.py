from django.urls import path
from .views import *

urlpatterns = [
    
    path("comments/" , CommentView.as_view() , name="comments"),
    path("comments/<int:pk>/" , CommentDetailView.as_view() , name="commentsdetail"),

    path("tasks/<int:pk>/comments/" , TaskCommentsList.as_view() , name="taskcommentslist"),


]