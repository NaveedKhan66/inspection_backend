from users.serializers import builder
from rest_framework import viewsets, mixins, generics
from rest_framework import permissions
from users.permissions import IsBuilder
from users.permissions import IsEmployee
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import status
from django.core.mail import send_mail
from inspection_backend.settings import EMAIL_HOST_USER
from inspection_backend.settings import RESET_PASSOWRD_LINK
from users.models import User
from users.filters import TradeFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

User = get_user_model()


class BuilderTradeListView(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    serializer_class = builder.BuilderTradeListSerializer
    permission_classes = [permissions.IsAuthenticated, IsBuilder | IsEmployee]
    queryset = User.objects.filter(user_type="trade")
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = TradeFilter

    def get_queryset(self):
        builder = None

        if self.request.user.user_type == "builder":
            builder = self.request.user.builder
        elif self.request.user.user_type == "employee":
            builder = self.request.user.employee.builder

        return super().get_queryset().filter(trade__builder=builder)


class OwnerInviteView(APIView):
    serializer_class = builder.OwnerInviteSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            home = serializer.validated_data["home"]
            owner = home.client
            if owner:
                if owner.client.is_invited:
                    text = "You've been invited by the builder to view inspections. You can use your created credentials to login into your account"
                    send_mail(
                        "Inspection Invitation",
                        text,
                        f"Builder Eye <{EMAIL_HOST_USER}>",
                        [owner.email],
                        fail_silently=False,
                    )
                else:
                    token = AccessToken.for_user(owner)
                    link = f"{RESET_PASSOWRD_LINK}?token={token}"
                    send_mail(
                        "Reset your password",
                        f"Click the link to set your password: {link}",
                        f"Builder Eye <{EMAIL_HOST_USER}>",
                        [owner.email],
                        fail_silently=False,
                    )
                    owner.client.is_invited = True
                    owner.client.save()

            return Response(
                {"message": "Invite sent successfully"}, status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
