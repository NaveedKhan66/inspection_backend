from rest_framework import serializers
from projects.models import Project, Home
from projects.serializers.admin import (
    ProjectAssigneeSerializer,
    ProjectBuilderSerializer,
)
from django.contrib.auth import get_user_model
from projects.serializers.admin import ClientforHomeSerializer


User = get_user_model()


class BuilderProjectsListSerializer(serializers.ModelSerializer):
    assignees = ProjectAssigneeSerializer(many=True)
    builder = ProjectBuilderSerializer()

    class Meta:
        model = Project
        fields = ["id", "name", "no_of_homes", "assignees", "builder", "status"]


class BuilderProjectAssigneeSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "phone_no", "role"]

    def get_role(self, obj):
        if obj.user_type == "employee":
            if obj.employee.role:
                return obj.employee.role


class BuilderProjectsRetrieveSerializer(serializers.ModelSerializer):
    assignees = BuilderProjectAssigneeSerializer(many=True)
    builder = ProjectBuilderSerializer()

    class Meta:
        model = Project
        fields = ["id", "name", "builder", "no_of_homes", "assignees", "vbn"]
