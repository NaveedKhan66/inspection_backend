from users.serializers import builder
from rest_framework import viewsets, mixins, generics
from rest_framework import permissions
from users.permissions import IsBuilder
from django.contrib.auth import get_user_model

User = get_user_model()


class BuilderTradeListView(generics.ListAPIView):
    serializer_class = builder.BuilderTradeListSerializer
    permission_classes = [permissions.IsAuthenticated, IsBuilder]
    queryset = User.objects.filter(user_type="trade")

    def get_queryset(self):
        return super().get_queryset().filter(trade__builder__user=self.request.user)
