from inspections.serializers.builder import DeficiencyListSerializer
from rest_framework import generics
from users.permissions import IsTrade
from inspections.models import Deficiency, DeficiencyUpdateLog
from inspections.serializers import trade
from django_filters.rest_framework import DjangoFilterBackend
from inspections.filters import DeficiencyFilter


class TradeDeficiencyListView(generics.ListAPIView):
    serializer_class = DeficiencyListSerializer
    permission_classes = [IsTrade]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DeficiencyFilter

    queryset = Deficiency.objects.all()

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(trade=self.request.user)
            .order_by("-updated_at")
        )


class DeficiencyUpdateLogListView(generics.ListAPIView):
    serializer_class = trade.DeficiencyUpdateLogSerializer
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        deficiency_id = self.kwargs.get("id")
        return DeficiencyUpdateLog.objects.filter(deficiency_id=deficiency_id).order_by(
            "-created_at"
        )
