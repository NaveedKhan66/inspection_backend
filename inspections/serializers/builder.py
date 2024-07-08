from inspections.models import (
    Inspection,
    Deficiency,
    DefImage,
    HomeInspectionReview,
    HomeInspection,
)
from rest_framework import serializers
from datetime import date
from django.contrib.auth import get_user_model
from projects.models import Home

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
        ]
        read_only_fields = ["home_inspection", "created_at", "is_reviewed"]

    def validate(self, attrs):
        validated_data = super().validate(attrs)

        # trade validations
        trade = validated_data.get("trade")
        if trade:
            if trade.user_type != "trade":
                raise serializers.ValidationError(
                    {"detail": "Deficiecy can only be assigned to a trade."}
                )
            if trade.trade.builder.user != self.context["request"].user:
                raise serializers.ValidationError(
                    {"detail": "Trade belongs to another builder."}
                )

        return validated_data

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        inspection = validated_data.pop("inspection")
        home = validated_data.pop("home")
        home_inspection = None

        if HomeInspection.objects.filter(home=home, inspection=inspection).exists():
            home_inspection = HomeInspection.objects.filter(
                home=home, inspection=inspection
            ).first()
        else:
            home_inspection = HomeInspection.objects.create(
                home=home, inspection=inspection
            )

        validated_data["home_inspection"] = home_inspection

        deficiency = Deficiency.objects.create(**validated_data)
        for image_data in images_data:
            DefImage.objects.create(deficiency=deficiency, **image_data)
        return deficiency

    def update(self, instance, validated_data):
        images_data = validated_data.pop("images", [])

        super().update(instance, validated_data)

        for image_data in images_data:
            DefImage.objects.create(deficiency=instance, **image_data)

        return instance

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
    inspection = serializers.PrimaryKeyRelatedField(
        queryset=Inspection.objects.all(), write_only=True
    )
    home = serializers.PrimaryKeyRelatedField(
        queryset=Home.objects.all(), write_only=True
    )

    class Meta:
        model = HomeInspectionReview
        fields = "__all__"
        read_only_fields = ["home_inspection"]

    def create(self, validated_data):
        inspection = validated_data.pop("inspection")
        home = validated_data.pop("home")
        home_inspection = HomeInspection.objects.filter(
            inspection=inspection, home=home
        ).first()
        if not home_inspection:
            raise serializers.ValidationError(
                {"detail": "This Home inspection doesn't exist"}
            )
        validated_data["home_inspection"] = home_inspection
        try:
            return HomeInspectionReview.objects.get(home_inspection=home_inspection)
        except HomeInspectionReview.DoesNotExist:
            return HomeInspectionReview.objects.create(**validated_data)


class DeficiencyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    deficiency_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False
    )

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
        home_owner = instance.home.client
        if home_owner:
            representation["owner"] = home_owner.get_full_name()
        return representation
