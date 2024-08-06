from rest_framework import serializers
from django.contrib.auth import get_user_model
from projects.models import Home

User = get_user_model()


class BuilderTradeListSerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField()
    incomplete_items = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "services",
            "incomplete_items",
        ]

    def get_services(self, obj):
        return obj.trade.services

    def get_incomplete_items(self, obj):
        incomplete_statuses = ["incomplete", "pending_approval"]
        return obj.deficiencies.filter(status__in=incomplete_statuses).count()


class OwnerInviteSerializer(serializers.Serializer):
    home = serializers.PrimaryKeyRelatedField(queryset=Home.objects.all())
