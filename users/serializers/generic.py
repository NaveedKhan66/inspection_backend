from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from inspection_backend.settings import EMAIL_HOST_USER
from inspection_backend.settings import RESET_PASSOWRD_LINK
from users.models import Builder
from users.models import Trade
from users.models import Client
from users.models import BuilderEmployee
from users.models import BlacklistedToken
from users.utils import (
    send_reset_email,
    create_employee_for_builder,
    set_password_for_employee,
    send_trade_welcome_email,
)
from django.db import transaction

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        attrs["email"] = attrs["email"].lower()
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


class AdminCreateUserSerializer(serializers.ModelSerializer):
    """Serializer to create multiple builders and clients"""

    user_type = serializers.ChoiceField(choices=User.USER_TYPES)
    builder = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(user_type="builder"), required=False
    )
    role = serializers.CharField(max_length=255, required=False)
    services = serializers.CharField(max_length=128, required=False)

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
            "phone_no",
            "province",
            "city",
            "postal_code",
            "profile_picture",
            "builder",
            "role",
            "services",
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
        elif user.user_type == "employee":
            raise serializers.ValidationError(
                {"detail": "Builder employees cannot create another user"}
            )
        elif user.user_type == "builder":
            raise serializers.ValidationError(
                {
                    "detail": "Builders can only create Trades but not through this endpoint"
                }
            )
        elif user.user_type == "admin" and validated_data.get("user_type") == "trade":
            raise serializers.ValidationError({"detail": "Admin cannot create Trades"})

        # Builder id is required to create an employee
        if validated_data.get("user_type") == "employee" and not validated_data.get(
            "builder"
        ):
            raise serializers.ValidationError(
                {"detail": "Builder is required when creating an employee"}
            )
        return validated_data

    @transaction.atomic()
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["email"],
            email=validated_data["email"],
            address=validated_data.get("address"),
            website=validated_data.get("website"),
            province=validated_data.get("province"),
            city=validated_data.get("city"),
            user_type=validated_data.get("user_type"),
            postal_code=validated_data.get("postal_code"),
            profile_picture=validated_data.get("profile_picture"),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            phone_no=validated_data.get("phone_no"),
        )
        user.set_unusable_password()
        user.save()

        user_type = validated_data.get("user_type")
        request = self.context.get("request")

        if user_type == "builder":
            builder = Builder.objects.create(user=user)
            create_employee_for_builder(user)

        elif user_type == "client":
            client = Client.objects.create(user=user)

        elif user_type == "employee":
            builder_user = validated_data.get("builder")
            role = validated_data.get("role")
            employee = BuilderEmployee.objects.create(
                user=user, builder=builder_user.builder, role=role
            )

        # Create a JWT token
        token = AccessToken.for_user(user)

        # Send email with token
        send_reset_email(user.email, str(token))

        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.user_type == "builder" or instance.user_type == "client":
            representation.pop("builder")

        if instance.user_type == "employee":
            representation["role"] = instance.employee.role

        return representation


def validate_token_not_blacklisted(value):
    if BlacklistedToken.objects.filter(token=value).exists():
        raise serializers.ValidationError(
            "This token has already been used and is no longer valid."
        )
    return value


class BuilderCreateUserSerializer(serializers.Serializer):
    """Serializer to create or add multiple trades"""

    email = serializers.EmailField()
    services = serializers.CharField(max_length=128, required=False)
    first_name = serializers.CharField(required=False)

    def validate_email(self, value):
        email = value.lower()
        user = User.objects.filter(email=email).first()

        if user and user.user_type != "trade":
            raise serializers.ValidationError(
                "This email is already registered with a different user type"
            )

        return email

    def validate(self, attrs):
        super().validate(attrs)
        request = self.context.get("request")

        if request.user.user_type != "builder":
            raise serializers.ValidationError(
                {"detail": "Only builders can create or add trades"}
            )

        return super().validate(attrs)

    @transaction.atomic()
    def create(self, validated_data):
        email = validated_data["email"]
        request = self.context.get("request")
        builder = request.user.builder

        # Check if trade user already exists
        existing_user = User.objects.filter(email=email).first()

        if existing_user:
            # User exists and must be trade (due to validation)
            trade = existing_user.trade
            trade.builder.add(builder)
            send_trade_welcome_email(trade, builder)
            return existing_user

        # Create new trade user
        user = User.objects.create(
            username=email,
            email=email,
            user_type="trade",
            first_name=validated_data.get("first_name", ""),
        )
        user.set_unusable_password()
        user.save()

        # Create trade and associate with builder
        trade = Trade.objects.create(user=user, services=validated_data.get("services"))
        trade.builder.add(builder)

        # Send reset password email
        token = AccessToken.for_user(user)
        send_reset_email(user.email, str(token), builder, trade, is_trade=True)
        send_trade_welcome_email(trade, builder)
        return user

    class Meta:
        model = User
        fields = ["id", "first_name", "email", "services"]


class SetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(validators=[validate_token_not_blacklisted])
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

        if user.user_type == "builder":
            # change password for the same employee instance as well
            set_password_for_employee(user, self.validated_data["password"])
        # Blacklist the token
        BlacklistedToken.objects.create(token=self.validated_data["token"])


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class UserProfileSerializer(serializers.ModelSerializer):
    version = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "profile_picture",
            "version",
        ]
        read_only_fields = ["id", "email", "version"]

    def get_version(self, obj):
        return "1.3.0"
