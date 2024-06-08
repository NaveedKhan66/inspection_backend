from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from inspection_backend.settings import EMAIL_HOST
from inspection_backend.settings import RESET_PASSOWRD_LINK
from users.models import Builder
from users.models import Trade
from users.models import Client

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        user_type = self.user.user_type
        # Add custom data
        data.update(
            {
                "id": self.user.id,
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "first_login": self.user.first_login,
                "user_type": user_type,
                "profile_picture": self.user.profile_picture,
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

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "user_type",
            "first_name",
            "last_name",
            "profile_picture",
        ]
        extra_kwargs = {
            "email": {"read_only": True},
            "id": {"read_only": True},
            "user_type": {"read_only": True},
        }


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer to create multiple builders clients and trades"""

    user_type = serializers.ChoiceField(choices=User.USER_TYPES)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "user_type",
            "address",
            "website",
            "province",
            "city",
            "postal_code",
            "profile_picture",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "first_name": {"required": False},
            "last_name": {"required": False},
            "address": {"required": False},
            "website": {"required": False},
            "province": {"required": False},
            "city": {"required": False},
            "postal_code": {"required": False},
            "profile_picture": {"required": False},
        }

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
            address=validated_data.get("address"),
            website=validated_data.get("website"),
            province=validated_data.get("province"),
            city=validated_data.get("city"),
            postal_code=validated_data.get("postal_code"),
            profile_picture=validated_data.get("profile_picture"),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        user.set_unusable_password()
        user.save()

        user_type = validated_data.get("user_type")
        request = self.context.get("request")

        if user_type == "builder":
            builder = Builder.objects.create(user=user)
        elif user_type == "client":
            client = Client.objects.create(user=user)
        elif user_type == "trade":
            trade = Trade.objects.create(user=user, builder=request.user.builder)

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
