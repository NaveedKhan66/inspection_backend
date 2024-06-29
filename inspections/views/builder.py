from inspections.models import Inspection, Deficiency, DefImage
from rest_framework import viewsets, generics
from users.permissions import IsBuilder
from users.models import User
from inspections.serializers import builder
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


class InspectionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsBuilder]
    serializer_class = builder.InspectionSerializer
    queryset = Inspection.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(builder=self.request.user)

    def perform_create(self, serializer):
        serializer.save(builder=self.request.user)


class DeficiencyViewSet(viewsets.ModelViewSet):
    serializer_class = builder.DeficiencySerializer
    permission_classes = [IsAuthenticated, IsBuilder]

    def get_queryset(self):
        inspection_id = self.kwargs.get("inspection_id")
        builder = self.request.user
        return Deficiency.objects.filter(
            inspection_id=inspection_id, inspection__builder=builder
        )

    def get_serializer_class(self):
        serializer_class = super().get_serializer_class()

        if self.request.method == "GET":
            if not self.kwargs.get("pk"):
                serializer_class = builder.DeficiencyListSerializer

        return serializer_class

    def perform_create(self, serializer):
        inspection_id = self.kwargs.get("inspection_id")
        inspection = get_object_or_404(Inspection, id=inspection_id)
        serializer.save(inspection=inspection)


class DefImageDeleteView(generics.DestroyAPIView):
    serializer_class = builder.DefImageSerializer
    permission_class = (IsAuthenticated, IsBuilder)
    queryset = DefImage.objects.all()

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(deficiency__inspection__builder=self.request.user)
        )
