from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from inspection_backend.settings import EMAIL_HOST
from inspection_backend.settings import RESET_PASSOWRD_LINK

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


class UpdateUserDetailSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    profile_picture = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "profile_picture"]


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer to create multiple builders clients and trades"""

    user_type = serializers.ChoiceField(choices=User.USER_TYPES)

    class Meta:
        model = User
        fields = ["email", "user_type"]

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        request = self.context.get("request")
        user = request.user

        if user.user_type == "client":
            raise serializers.ValidationError(
                {"detail": "Clients cannot create another user"}
            )
        elif (
            user.user_type == "builder"
            and not validated_data.get("user_type") == "trade"
        ):
            raise serializers.ValidationError(
                {"detail": "Builders can only create Trades"}
            )
        return validated_data

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["email"],
            email=validated_data["email"],
            user_type=validated_data["user_type"],
        )
        user.set_unusable_password()
        user.save()

        # Create a JWT token
        token = AccessToken.for_user(user)

        # Send email with token
        self.send_reset_email(user.email, str(token))

        return user

    def send_reset_email(self, email, token):

        from django.core.mail import send_mail

        link = f"{RESET_PASSOWRD_LINK}?token={token}"
        send_mail(
            "Reset your password",
            f"Click the link to set your password: {link}",
            EMAIL_HOST,
            [email],
            fail_silently=False,
        )


class SetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField()

    def validate_token(self, value):
        try:
            # Decode the token
            token = AccessToken(value)
            user_id = token["user_id"]
            self.user = User.objects.get(id=user_id)
        except Exception as e:
            raise serializers.ValidationError("Invalid token") from e

        return value

    def save(self):
        user = self.user
        user.set_password(self.validated_data["password"])
        user.save()
