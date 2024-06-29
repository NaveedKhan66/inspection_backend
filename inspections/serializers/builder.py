from inspections.models import Inspection, Deficiency, DefImage, DeficiencyReview
from rest_framework import serializers
from datetime import date
from django.contrib.auth import get_user_model

User = get_user_model()


class InspectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Inspection
        fields = "__all__"
        read_only_fields = ["builder"]


class DefImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefImage
        fields = ["id", "image"]
        read_only_fields = ["id"]


class DeficiencySerializer(serializers.ModelSerializer):
    images = DefImageSerializer(many=True, required=False)

    class Meta:
        model = Deficiency
        fields = [
            "id",
            "inspection",
            "location",
            "trade",
            "project",
            "home",
            "description",
            "images",
            "created_at",
            "status",
            "is_reviewed",
        ]
        read_only_fields = ["inspection", "created_at", "is_reviewed"]

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

        home = validated_data.get("home")
        project = validated_data.get("project")

        if home.project != project:
            raise serializers.ValidationError(
                {"detail": "Deficiency and home must belong to the same project."}
            )

        return validated_data

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
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


class DeficiencyListSerializer(serializers.ModelSerializer):
    outstanding_days = serializers.SerializerMethodField()

    class Meta:
        model = Deficiency
        exclude = ["project", "home"]

    def get_outstanding_days(self, obj):
        if obj.status == "complete":
            return 0
        else:
            delta = date.today() - obj.created_at
            return delta.days


class DefReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeficiencyReview
        fields = "__all__"

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        request = self.context.get("request")
        builder = request.user

        deficiency = validated_data.get("deficiency")

        if deficiency.home.project.builder != builder:
            raise serializers.ValidationError(
                {"detail": "Deficiency belongs to another builder."}
            )

        return validated_data


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
