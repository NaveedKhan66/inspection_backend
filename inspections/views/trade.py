from inspections.serializers.builder import DeficiencyListSerializer
from rest_framework import generics
from users.permissions import IsTrade
from inspections.models import Deficiency


class TradeDeficiencyListView(generics.ListAPIView):
    serializer_class = DeficiencyListSerializer
    permission_classes = [IsTrade]

    queryset = Deficiency.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(trade=self.request.user)
