from rest_framework_simplejwt.views import TokenObtainPairView
from users.serializers.generic import CustomTokenObtainPairSerializer
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from users.serializers.generic import UpdateFirstLoginSerializer
from users.serializers.generic import UpdateUserDetailSerializer
from users.serializers.generic import CreateUserSerializer
from users.serializers.generic import SetPasswordSerializer
from users.serializers.generic import ForgetPasswordSerializer
from users.serializers.generic import UserProfileSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import AccessToken
from users.utils import send_reset_email


User = get_user_model()


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
    Admin can create Builders, Clients.
    Builders can create Trades
    """

    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = [permissions.IsAuthenticated]


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


class ForgetPasswordView(APIView):
    serializer_class = ForgetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.data.get("email", "").lower()
            user = get_object_or_404(User, email=email)
            token = AccessToken.for_user(user)

            send_reset_email(email, str(token))
            return Response(
                {"detail": "Password reset link has been sent to your email."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileUpdateRetrieveView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
