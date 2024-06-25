from django.contrib.auth.models import User
from rest_framework import generics, permissions
from users.serializers.admin import AdminPasswordResetSerializer
from users.serializers.admin import AdminBuilderSerializer
from users.serializers.admin import AdminBuilderEmployeeSerializer
from rest_framework import mixins
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from users.models import BuilderEmployee
from django.shortcuts import get_object_or_404


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


class AdminBuilderEmployeeListView(generics.ListAPIView):
    """View to list builder employees for admin"""

    serializer_class = AdminBuilderEmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_queryset(self):
        builder_id = self.kwargs.get("id")
        user = get_object_or_404(User, id=builder_id)

        if user.user_type != "builder":
            return BuilderEmployee.objects.none()

        queryset = BuilderEmployee.objects.filter(builder=user.builder)
        return queryset


class AdminBuilderEmployeeRetrieveUpdateDeleteView(
    generics.RetrieveAPIView, generics.DestroyAPIView, generics.UpdateAPIView
):
    """View to retrieve builder employees for admin"""

    serializer_class = AdminBuilderEmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    queryset = BuilderEmployee.objects.all()
    lookup_field = "user__id"
