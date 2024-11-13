from rest_framework import serializers
from inspections.models import DeficiencyUpdateLog


class DeficiencyUpdateLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeficiencyUpdateLog
        fields = ["id", "actor_name", "created_at", "description"]
