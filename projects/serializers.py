from rest_framework import serializers
from projects.models import Project
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
            "assignees": {"read_only": True},
        }

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        builder_user = validated_data.get("builder")

        if builder_user:
            if builder_user.user_type != "builder":
                raise ValidationError(
                    {"detail": "Only builder can be assigned to projects"}
                )

        return validated_data


class ProjectAssigneeUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer to add and remove assignees from the project
    """

    assignees = serializers.ListField(
        child=serializers.UUIDField(format="hex_verbose"),
        write_only=True,
        required=False,
    )
    remove_assignee = serializers.UUIDField(
        format="hex_verbose", write_only=True, required=False
    )

    class Meta:
        model = Project
        fields = ["assignees", "remove_assignee"]

    def update(self, instance, validated_data):
        # addition
        assignees = validated_data.pop("assignees", None)
        if assignees:
            users = User.objects.filter(id__in=assignees, user_type="employee")
            instance.assignees.add(*users)

        # Removal
        remove_assignee = validated_data.pop("remove_assignee", None)
        if remove_assignee:
            try:
                user = User.objects.get(id=remove_assignee)
                instance.assignees.remove(user)
            except User.DoesNotExist:
                pass

        return super().update(instance, validated_data)


class AssigneeSerializer(serializers.ModelSerializer):
    """General assignee serializer for projects"""

    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "profile_picture", "role"]

    def get_role(self, obj):
        if obj.user_type == "employee":
            if obj.employee.role:
                return obj.employee.role
        return None


class ProjectAssigneeListSerializer(serializers.ModelSerializer):
    """Serializer to list all assignees of a project"""

    assignees = AssigneeSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ["assignees"]
