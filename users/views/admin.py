from django.contrib.auth.models import User
from rest_framework import generics, permissions
from users.serializers.admin import AdminPasswordResetSerializer
from users.serializers.admin import AdminBuilderSerializer
from rest_framework import mixins
from rest_framework import viewsets
from django.contrib.auth import get_user_model


User = get_user_model()


class AdminPasswordResetView(generics.UpdateAPIView):
    """View to reset admin password upon first login"""

    queryset = User.objects.all()
    serializer_class = AdminPasswordResetSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_object(self):
        return self.request.user


class AdminBuilderViewset(
    viewsets.GenericViewSet,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
):
    """
    This is for the admin to interact with users
    Create is not allowed on this because another API is used for it
    """

    queryset = User.objects.filter(user_type="builder")
    serializer_class = AdminBuilderSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
