
from rest_framework.serializers import ModelSerializer

from rest_framework import serializers
from .models import User



class UserSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = [ "id",
            "username",
            "password",
            "email",
            "first_name",
            "last_name",
            "role",
            "organization",]
    
    def validate(self,validated_data):

        request = self.context['request']

        user = request.user

        request_role = validated_data.get('role')

        if (user.role == 'organization_admin' and request_role not in ['project_manager','team_member']):
            raise serializers.ValidationError("You can only create project managers and team members")
        return validated_data
   

    
    def create(self , validated_data):
        return User.objects.create_user(**validated_data)



class UserManageSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [ "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "organization",]

        read_only_fields = [
            "role",
            "organization",
        ]


