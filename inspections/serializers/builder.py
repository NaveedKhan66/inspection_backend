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
from django.db import transaction
from django.utils.text import Truncator
from inspections.utils import send_inspection_report_email
import threading
from inspections.utils import get_notification_users
from inspections.utils import DeficiencyUpdateLogsCreationThread
from inspections.utils import DeficiencyNotificationsCreationThread

User = get_user_model()


class InspectionSerializer(serializers.ModelSerializer):
    total_inspections = serializers.SerializerMethodField()

    class Meta:
        model = Inspection
        fields = "__all__"
        read_only_fields = ["builder", "no_of_def"]

    def get_total_inspections(self, obj):
        return HomeInspection.objects.filter(inspection=obj).count()


class DefImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefImage
        fields = ["id", "image"]
        read_only_fields = ["id"]


class DefCreateSerializer(serializers.ModelSerializer):
    images = DefImageSerializer(many=True, required=False)

    class Meta:
        model = Deficiency
        fields = [
            "id",
            "location",
            "trade",
            "description",
            "status",
            "is_reviewed",
            "images",
            "created_at",
        ]

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        deficiency = Deficiency.objects.create(**validated_data)

        for image_data in images_data:
            DefImage.objects.create(deficiency=deficiency, **image_data)

        return deficiency


class HomeInspectionCreateSerializer(serializers.ModelSerializer):
    deficiencies = DefCreateSerializer(many=True, required=False)

    class Meta:
        model = HomeInspection
        fields = [
            "id",
            "home",
            "inspection",
            "owner_visibility",
            "deficiencies",
            "created_at",
        ]
        write_only_fields = ["home", "inspection"]

    def create(self, validated_data):
        deficiencies_data = validated_data.pop("deficiencies", [])
        user = self.context["request"].user
        builder_user = validated_data.get("inspection").builder
        notification_users = get_notification_users(user)

        # Create HomeInspection instance
        home_inspection = HomeInspection.objects.create(**validated_data)

        # Create associated Deficiencies
        for deficiency_data in deficiencies_data:
            images_data = deficiency_data.pop("images", [])
            deficiency = Deficiency.objects.create(
                home_inspection=home_inspection, **deficiency_data
            )
            changes = [
                f"{user.get_full_name()} Created a new Deficiency: {deficiency.id}"
            ]
            # Create notifications
            notifications_thread = DeficiencyNotificationsCreationThread(
                changes, deficiency, user, notification_users, builder_user
            )
            notifications_thread.start()

            # Create associated DefImages
            for image_data in images_data:
                DefImage.objects.create(deficiency=deficiency, **image_data)

        return home_inspection

    def validate(self, data):
        """
        Custom validation to ensure home and inspection are valid
        """
        if not data.get("home"):
            raise serializers.ValidationError("Home is required")
        if not data.get("inspection"):
            raise serializers.ValidationError("Inspection is required")
        return data


class DeficiencySerializer(serializers.ModelSerializer):
    next = serializers.SerializerMethodField()
    previous = serializers.SerializerMethodField()
    images = DefImageSerializer(many=True)
    city = serializers.SerializerMethodField()
    province = serializers.SerializerMethodField()

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
            "home_inspection",
            "next",
            "previous",
            "city",
            "province",
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

            if user not in trade.trade.builder.user.all():
                raise serializers.ValidationError(
                    {"detail": "Trade belongs to another builder."}
                )

        return validated_data

    def create(self, validated_data):
        """Overriding this because this is not being used"""
        pass

    @transaction.atomic
    def update(self, instance, validated_data):
        request = self.context.get("request")
        actor = request.user if request else None

        # populate users to which the notification will be sent
        builder_user = instance.home_inspection.inspection.builder
        notification_users = get_notification_users(request.user)

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
            old_desc = Truncator(instance.description).chars(300)
            new_desc = Truncator(validated_data["description"]).chars(300)
            changes.append(f"Description Changed: From '{old_desc}' to '{new_desc}'")

        # Check for status change
        if "status" in validated_data and validated_data["status"] != instance.status:
            changes.append(
                f"Status Changed: {instance.status} to {validated_data['status']}"
            )

        # Check for image additions
        images_data = validated_data.pop("images", [])
        print(images_data)
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
            print(image_data)
            DefImage.objects.create(deficiency=instance, **image_data)

        if changes:
            # Create logs and notifications in a different thread for optimisation
            logs_thread = DeficiencyUpdateLogsCreationThread(changes, instance, actor)
            notifications_thread = DeficiencyNotificationsCreationThread(
                changes, instance, actor, notification_users, builder_user
            )
            logs_thread.start()
            notifications_thread.start()

        return instance

    def get_filtered_queryset(self):
        request = self.context.get("request")
        view = self.context.get("view")
        queryset = view.get_queryset() if view else None

        if queryset is not None and request is not None:
            return view.filter_queryset(queryset)
        return None

    def get_next(self, obj):
        qs = self.get_filtered_queryset()
        if qs is None:
            return None

        # Ensure the queryset is ordered as per the listing
        qs = qs.order_by("updated_at")

        # Find the index of the current object
        try:
            current_index = list(qs).index(obj)
            # Get the next object if it exists
            if current_index - 1 >= 0:
                return qs[current_index - 1].id
        except (ValueError, IndexError):
            return None

    def get_previous(self, obj):
        qs = self.get_filtered_queryset()
        if qs is None:
            return None

        # Ensure the queryset is ordered as per the listing
        qs = qs.order_by("updated_at")

        # Find the index of the current object
        try:
            current_index = list(qs).index(obj)
            # Get the previous object if it exists
            if current_index + 1 < len(qs):
                return qs[current_index + 1].id
        except (ValueError, IndexError):
            return None

    def get_city(self, obj):
        return obj.home_inspection.home.project.city

    def get_province(self, obj):
        return obj.home_inspection.home.project.province

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["trade"] = {
            "id": instance.trade.id,
            "name": instance.trade.get_full_name(),
        }
        return representation


class DeficiencyListSerializer(serializers.ModelSerializer):
    outstanding_days = serializers.SerializerMethodField()
    home_address = serializers.SerializerMethodField()
    inspection_type = serializers.SerializerMethodField()
    province = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()

    class Meta:
        model = Deficiency
        exclude = ["home_inspection"]

    def get_outstanding_days(self, obj):
        if obj.completion_date:
            delta = obj.completion_date - obj.created_at
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

    def get_home_address(self, obj):
        home = obj.home_inspection.home
        home_address = " ".join(
            [
                a
                for a in [
                    home.street_no if home.street_no else "",
                    home.address if home.address else "",
                    home.city if home.city else "",
                ]
                if a
            ]
        )
        return home_address

    def get_inspection_type(self, obj):
        return obj.home_inspection.inspection.name

    def get_province(self, obj):
        return obj.home_inspection.home.project.province

    def get_city(self, obj):
        return obj.home_inspection.home.project.city


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
