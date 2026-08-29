from django.urls import path
from .views import *

urlpatterns = [
    
    path("tasks/" , TasksView.as_view() , name="tasks"),
    path("tasks/<int:pk>/" , TasksDetailView.as_view() , name="tasks-detail")

]