from inspections.models import Inspection, Deficiency, DefImage
from rest_framework import viewsets
from users.permissions import IsBuilder
from users.models import User
from inspections.serializers import builder
from rest_framework.permissions import IsAuthenticated


class InspectionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsBuilder]
    serializer_class = builder.InspectionSerializer
    queryset = Inspection.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(builder=self.request.user)

    def perform_create(self, serializer):
        serializer.save(builder=self.request.user)
