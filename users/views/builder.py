from users.serializers import builder
from rest_framework import viewsets, mixins, generics
from rest_framework import permissions
from users.permissions import IsBuilder
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import status
from django.core.mail import send_mail
from inspection_backend.settings import EMAIL_HOST
from inspection_backend.settings import RESET_PASSOWRD_LINK

User = get_user_model()


class BuilderTradeListView(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    serializer_class = builder.BuilderTradeListSerializer
    permission_classes = [permissions.IsAuthenticated, IsBuilder]
    queryset = User.objects.filter(user_type="trade")

    def get_queryset(self):
        return super().get_queryset().filter(trade__builder__user=self.request.user)


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
                        EMAIL_HOST,
                        [owner.email],
                        fail_silently=False,
                    )
                else:
                    token = AccessToken.for_user(owner)
                    link = f"{RESET_PASSOWRD_LINK}?token={token}"
                    send_mail(
                        "Reset your password",
                        f"Click the link to set your password: {link}",
                        EMAIL_HOST,
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
