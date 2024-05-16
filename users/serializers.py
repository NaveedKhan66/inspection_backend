from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from project_utils.serializers import SlugToIntChoiceField

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


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        user_type = User.USER_TYPES.get_slug_by_value(self.user.user_type)
        # Add custom data
        data.update(
            {
                "id": self.user.id,
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "first_login": self.user.first_login,
                "user_type": user_type,
            }
        )

        return data


class UpdateFirstLoginSerializer(serializers.ModelSerializer):
    """Serializer to change the first_login to False"""

    first_login = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ["first_login"]
