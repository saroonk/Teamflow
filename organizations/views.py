from django.shortcuts import render

# Create your views here.

from .serializer import OrganizationListSerializer
from rest_framework.generics import *


from .permissions import IsOrganizationManager
from .models import *

class OrganizationList(ListCreateAPIView):
    serializer_class = OrganizationListSerializer
    queryset = Organizations.objects.all()
    permission_classes = [IsOrganizationManager]
    

class OrganizationListManage(RetrieveUpdateDestroyAPIView):
    serializer_class = OrganizationListSerializer
    queryset = Organizations.objects.all()
    permission_classes = [IsOrganizationManager]
