from rest_framework import serializers
from inspections.models import DeficiencyUpdateLog


class DeficiencyUpdateLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeficiencyUpdateLog
        fields = ["id", "actor_name", "created_at", "description"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["created_at"] = instance.created_at.strftime("%d %B %Y")
        return representation
