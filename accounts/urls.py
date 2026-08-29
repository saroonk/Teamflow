from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView


from .views import *

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    path("myprofile/", MeView.as_view(), name="me"),
    path("users/" , Users.as_view(), name = "Users"),
    path("users/<int:pk>/" , UsersManage.as_view(), name = "UsersManage"),


    
]