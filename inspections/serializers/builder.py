from inspections.models import Inspection, Deficiency, DefImage
from rest_framework import serializers


class InspectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Inspection
        fields = "__all__"
        read_only_fields = ["builder"]
