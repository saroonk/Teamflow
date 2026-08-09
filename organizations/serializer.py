from rest_framework.serializers import ModelSerializer

from .models import Organizations



class OrganizationListSerializer(ModelSerializer):
    class Meta:
        model = Organizations
        fields = ['id','name','description']