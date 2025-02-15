from django.contrib.auth.models import User
from rest_framework import generics, permissions
from users.serializers.admin import AdminPasswordResetSerializer
from users.serializers.admin import AdminBuilderSerializer
from users.serializers.admin import AdminBuilderEmployeeSerializer
from users.serializers.admin import UserSerializer
from rest_framework import mixins
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from users.models import BuilderEmployee
from django.shortcuts import get_object_or_404
from users.permissions import IsBuilder
from rest_framework.response import Response
from rest_framework import status


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


class UserDeleteView(generics.DestroyAPIView):
    """View to delete users and handle trade removal"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.IsAdminUser | IsBuilder,
    ]

    def delete(self, request, *args, **kwargs):
        user = self.get_object()

        # If user is a trade and requester is a builder
        if user.user_type == "trade" and request.user.user_type == "builder":
            trade = user.trade
            builder = request.user.builder

            # Remove association with current builder
            trade.builder.remove(builder)

            # If trade is not associated with any builders, delete the trade user
            if trade.builder.count() == 0:
                user.delete()
                return Response(
                    {
                        "detail": "Trade has been deleted as it was not associated with any other builders."
                    },
                    status=status.HTTP_204_NO_CONTENT,
                )

            return Response(
                {"detail": "Trade has been removed from your list."},
                status=status.HTTP_200_OK,
            )

        # For admin or other user types, proceed with normal deletion
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
