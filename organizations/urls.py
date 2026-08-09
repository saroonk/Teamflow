from django.contrib import admin
from django.urls import path,include

from .views import *
urlpatterns = [
    path('organizations/' , OrganizationList.as_view() , name = "OrganizationList"),
    path('organizations/<int:pk>/' , OrganizationListManage.as_view() , name = "OrganizationListManage")



    
]