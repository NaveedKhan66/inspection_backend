from django.contrib.auth.models import User
from users.models import BuilderEmployee
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class AdminPasswordResetSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["new_password", "confirm_password"]

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance


class AdminBuilderSerializer(serializers.ModelSerializer):

    no_of_projects = serializers.SerializerMethodField(read_only=True)
    team = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "user_type",
            "first_name",
            "last_name",
            "address",
            "website",
            "province",
            "city",
            "postal_code",
            "profile_picture",
            "first_login",
            "no_of_projects",
            "team",
            "phone_no",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "email": {"read_only": True},
            "user_type": {"read_only": True},
            "first_login": {"read_only": True},
        }

    def get_no_of_projects(self, obj):
        return obj.projects.count()

    def get_team(self, obj):
        return obj.builder.employees.count()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_no",
            "profile_picture",
        ]

        extra_kwargs = {
            "id": {"read_only": True},
            "email": {"read_only": True},
        }


class AdminBuilderEmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = BuilderEmployee
        fields = ["user", "role"]
