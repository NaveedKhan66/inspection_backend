from django.contrib.auth.models import User
from rest_framework import generics, permissions
from users.serializers import AdminPasswordResetSerializer
from users.serializers import CustomTokenObtainPairSerializer
from users.serializers import UpdateFirstLoginSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
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
