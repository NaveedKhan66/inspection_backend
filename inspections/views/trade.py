from inspections.serializers.builder import DeficiencyListSerializer
from rest_framework import generics
from users.permissions import IsTrade
from inspections.models import Deficiency, DeficiencyUpdateLog
from inspections.serializers import trade


class TradeDeficiencyListView(generics.ListAPIView):
    serializer_class = DeficiencyListSerializer
    permission_classes = [IsTrade]

    queryset = Deficiency.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(trade=self.request.user)


class DeficiencyUpdateLogListView(generics.ListAPIView):
    serializer_class = trade.DeficiencyUpdateLogSerializer
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        deficiency_id = self.kwargs.get("id")
        return DeficiencyUpdateLog.objects.filter(deficiency_id=deficiency_id)
