from django.contrib.auth.models import User
from rest_framework import generics, permissions
from users.serializers import AdminPasswordResetSerializer
from users.serializers import CustomTokenObtainPairSerializer
from users.serializers import UpdateFirstLoginSerializer
from users.serializers import UpdateUserDetailSerializer
from users.serializers import UpdateUserSerializer
from users.serializers import CreateUserSerializer
from users.serializers import SetPasswordSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model


User = get_user_model()


class AdminPasswordResetView(generics.UpdateAPIView):
    """View to reset admin password upon first login"""

    queryset = User.objects.all()
    serializer_class = AdminPasswordResetSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_object(self):
        return self.request.user


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UpdateFirstLoginView(generics.UpdateAPIView):
    """Sets first_login to false"""

    queryset = User.objects.all()
    serializer_class = UpdateFirstLoginSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        return serializer.save(first_login=False)


class UpdateUserDetailView(generics.UpdateAPIView):
    """
    This is used just to update first_name, last_name and profile_picture
    of the user calling this API
    """

    queryset = User.objects.all()
    serializer_class = UpdateUserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class CreateUserView(generics.CreateAPIView):
    """
    Following users can create other users
    Admin: Builder, Client
    Builder: Trade
    """

    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = [permissions.IsAuthenticated]


class UpdateUserView(generics.UpdateAPIView):
    """
    This is used to update complete user details by the admin
    """

    queryset = User.objects.all()
    serializer_class = UpdateUserSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]


class SetUserPasswordView(generics.GenericAPIView):
    """
    Sets user password upon first_login
    """

    serializer_class = SetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password has been reset."}, status=status.HTTP_200_OK
        )
