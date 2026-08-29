from django.urls import path
from .views import *

urlpatterns = [
    
    path("projects/" , ProjectsView.as_view() , name="projects"),
    path("projects/<int:pk>/" , ProjectsDetailView.as_view() , name="projects-detail"),

    path("projects/<int:pk>/members/" , ProjectMembersView.as_view() , name="project-members")
]

