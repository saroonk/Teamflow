from django.shortcuts import render

# Create your views here.

from .serializer import UserSerializer,UserManageSerializer

from .models import User

from rest_framework.generics import ListAPIView,RetrieveAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView


from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.permissions import AllowAny ,IsAuthenticated

from .permissions import IsSystemAdmin,IsOrganizationAdmin,IsProjectManager,IsTeamMember,IsSystemOrOrganizationAdmin



class MeView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = UserSerializer



    def get_object(self):
        return self.request.user





class PermissionTestView(APIView):
    permission_classes = [IsTeamMember]

    def get(self, request):
        return Response({
            "message": "You are a System Admin!",
            "user": request.user.username,
            # "role": request.user.role,
        })





class Users(ListCreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return User.objects.all()

        return User.objects.filter(
            role__in=["project_manager", "team_member"]
        )
    permission_classes = [IsSystemOrOrganizationAdmin]


class UsersManage(RetrieveUpdateDestroyAPIView):
    serializer_class = UserManageSerializer
    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return User.objects.all()

        return User.objects.filter(
            role__in=["project_manager", "team_member"]
        )
    permission_classes = [IsSystemOrOrganizationAdmin]
