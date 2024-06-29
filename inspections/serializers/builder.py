from inspections.models import Inspection, Deficiency, DefImage
from rest_framework import serializers
from datetime import date


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
        ]
        read_only_fields = ["inspection", "created_at"]

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
