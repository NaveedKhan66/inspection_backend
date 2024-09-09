from inspections.models import (
    Inspection,
    Deficiency,
    DefImage,
    HomeInspectionReview,
    HomeInspection,
    DeficiencyNotification,
)
from rest_framework import serializers
from datetime import date
from django.contrib.auth import get_user_model
from projects.models import Home
from django.db import transaction
from django.utils.text import Truncator
from inspections.utils import send_inspection_report_email
import threading
from django.db.models import Q
from inspections.utils import get_notification_users
from inspections.utils import DeficiencyUpdateLogsCreationThread
from inspections.utils import DeficiencyNotificationsCreationThread

User = get_user_model()


class InspectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Inspection
        fields = "__all__"
        read_only_fields = ["builder", "no_of_def"]


class DefImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefImage
        fields = ["id", "image"]
        read_only_fields = ["id"]


class DeficiencySerializer(serializers.ModelSerializer):
    images = DefImageSerializer(many=True, required=False)
    home = serializers.PrimaryKeyRelatedField(
        queryset=Home.objects.all(), write_only=True
    )
    inspection = serializers.PrimaryKeyRelatedField(
        queryset=Inspection.objects.all(), write_only=True
    )
    owner_visibility = serializers.BooleanField(required=False, write_only=True)
    home_inspection = serializers.PrimaryKeyRelatedField(
        queryset=HomeInspection.objects.all(), allow_null=True
    )
    next = serializers.SerializerMethodField()
    previous = serializers.SerializerMethodField()

    class Meta:
        model = Deficiency
        fields = [
            "id",
            "location",
            "trade",
            "description",
            "images",
            "created_at",
            "status",
            "is_reviewed",
            "home",
            "inspection",
            "home_inspection",
            "owner_visibility",
            "next",
            "previous",
        ]
        read_only_fields = ["created_at", "is_reviewed"]

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        user = self.context["request"].user
        # trade validations
        trade = validated_data.get("trade")
        if trade:
            if trade.user_type != "trade":
                raise serializers.ValidationError(
                    {"detail": "Deficiency can only be assigned to a trade."}
                )

            if user.user_type == "employee":
                user = user.employee.builder.user

            if trade.trade.builder.user != user:
                raise serializers.ValidationError(
                    {"detail": "Trade belongs to another builder."}
                )

        return validated_data

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        inspection = validated_data.pop("inspection")
        home = validated_data.pop("home")
        owner_visibility = validated_data.pop("owner_visibility", False)

        home_inspection = validated_data.get("home_inspection")
        if not home_inspection:
            home_inspection = HomeInspection.objects.create(
                home=home, inspection=inspection, owner_visibility=owner_visibility
            )

        validated_data["home_inspection"] = home_inspection

        deficiency = Deficiency.objects.create(**validated_data)
        for image_data in images_data:
            DefImage.objects.create(deficiency=deficiency, **image_data)
        return deficiency

    @transaction.atomic
    def update(self, instance, validated_data):
        request = self.context.get("request")
        actor = request.user if request else None

        # populate users to which the notification will be sent
        builder_user, notification_users = get_notification_users(request.user)

        # Track changes
        changes = []

        # Check for location change
        if (
            "location" in validated_data
            and validated_data["location"] != instance.location
        ):
            changes.append(
                f"Location Changed: '{instance.location}' to '{validated_data['location']}'"
            )

        # Check for trade change
        if "trade" in validated_data and validated_data["trade"] != instance.trade:
            old_trade = instance.trade.get_full_name() if instance.trade else "None"
            new_trade = (
                validated_data["trade"].get_full_name()
                if validated_data["trade"]
                else "None"
            )
            changes.append(f"Trade Changed: {old_trade} to {new_trade}")

        # Check for description change
        if (
            "description" in validated_data
            and validated_data["description"] != instance.description
        ):
            old_desc = Truncator(instance.description).chars(30)
            new_desc = Truncator(validated_data["description"]).chars(30)
            changes.append(f"Description Changed: From '{old_desc}' to '{new_desc}'")

        # Check for status change
        if "status" in validated_data and validated_data["status"] != instance.status:
            changes.append(
                f"Status Changed: {instance.status} to {validated_data['status']}"
            )

        # Check for image additions
        images_data = validated_data.pop("images", [])
        if images_data:
            changes.append("Images Changed: New images added.")

        if "owner_visibility" in validated_data:
            owner_visibility = validated_data.pop("owner_visibility")
            instance.home_inspection.owner_visibility = owner_visibility
            instance.home_inspection.save()

        # Update the instance
        instance = super().update(instance, validated_data)

        # Create DefImage objects for new images
        for image_data in images_data:
            DefImage.objects.create(deficiency=instance, **image_data)

        if changes:
            logs_thread = DeficiencyUpdateLogsCreationThread(changes, instance, actor)
            notifications_thread = DeficiencyNotificationsCreationThread(
                changes, instance, actor, notification_users, builder_user
            )
            logs_thread.start()
            notifications_thread.start()

        return instance

    def get_next(self, obj):
        """
        Evaluting queryset again to get next and previous properly
        so that trade and client deficiencies don't collide with each other
        """
        try:
            user = self.context["request"].user
            qs = None
            if user.user_type == "builder" or user.user_type == "employee":

                if user.user_type == "employee":
                    user = user.employee.builder.user

                qs = Deficiency.objects.filter(
                    home_inspection__inspection__builder=user
                )
            elif user.user_type == "trade":
                qs = Deficiency.objects.filter(trade=user)

            return qs.filter(id__gt=obj.id).order_by("id").first().id
        except AttributeError:
            return None

    def get_previous(self, obj):
        try:
            user = self.context["request"].user
            qs = None
            if user.user_type == "builder" or user.user_type == "employee":

                if user.user_type == "employee":
                    user = user.employee.builder.user

                qs = Deficiency.objects.filter(
                    home_inspection__inspection__builder=user
                )
            elif user.user_type == "trade":
                qs = Deficiency.objects.filter(trade=user)

            return qs.filter(id__lt=obj.id).order_by("-id").first().id
        except AttributeError:
            return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["trade"] = {
            "id": instance.trade.id,
            "name": instance.trade.get_full_name(),
        }
        return representation


class DeficiencyListSerializer(serializers.ModelSerializer):
    outstanding_days = serializers.SerializerMethodField()

    class Meta:
        model = Deficiency
        exclude = ["home_inspection"]

    def get_outstanding_days(self, obj):
        if obj.status == "complete":
            return 0
        else:
            delta = date.today() - obj.created_at
            return delta.days

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["trade"] = {
            "id": instance.trade.id,
            "name": instance.trade.get_full_name(),
        }
        return representation


class InspectionReviewSerializer(serializers.ModelSerializer):
    inspector_name = serializers.CharField(max_length=128, required=False)

    class Meta:
        model = HomeInspectionReview
        fields = "__all__"

    def create(self, validated_data):
        inspector = validated_data.pop("inspector_name", "")
        review = super().create(validated_data)
        review.home_inspection.inspector = inspector
        review.home_inspection.save()
        request = self.context.get("request")
        home_inspection = review.home_inspection

        # send inspection report in background
        thread = threading.Thread(
            target=send_inspection_report_email,
            kwargs={"request": request, "home_inspection": home_inspection},
        )
        thread.start()

        return review


class DeficiencyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    deficiency_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False
    )
    due_date = serializers.DateField()

    def validate_deficiency_ids(self, value):
        # Check if all IDs correspond to existing Deficiency objects
        deficiencies = Deficiency.objects.filter(id__in=value)
        if deficiencies.count() != len(value):
            raise serializers.ValidationError("One or more deficiency IDs are invalid.")
        return value


class HomeInspectionListSerializer(serializers.ModelSerializer):

    class Meta:
        model = HomeInspection
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        inspection = instance.inspection
        representation["inspection"] = {"id": inspection.id, "name": inspection.name}

        if hasattr(instance, "review") and instance.review:
            representation["designate"] = instance.review.designate
        else:
            representation["designate"] = False
        home_owner = instance.home.client
        if home_owner:

            representation["owner"] = {
                "id": home_owner.id,
                "name": home_owner.get_full_name(),
            }
        return representation


class DeficiencyNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeficiencyNotification
        fields = "__all__"


class DeficiencyNotificationReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeficiencyNotification
        fields = ["read"]
        read_only_fields = ["read"]

    def update(self, instance, validated_data):
        instance.read = True
        instance.save()
        return instance
