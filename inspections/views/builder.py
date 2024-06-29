from inspections.models import Inspection, Deficiency, DefImage, HomeInspectionReview
from rest_framework import viewsets, generics
from users.permissions import IsBuilder
from users.models import User
from inspections.serializers import builder
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import date
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from inspection_backend.settings import EMAIL_HOST
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from inspections.filters import DeficiencyFilter


class InspectionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsBuilder]
    serializer_class = builder.InspectionSerializer
    queryset = Inspection.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(builder=self.request.user)

    def perform_create(self, serializer):
        serializer.save(builder=self.request.user)


class DeficiencyViewSet(viewsets.ModelViewSet):
    serializer_class = builder.DeficiencySerializer
    permission_classes = [IsAuthenticated, IsBuilder]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DeficiencyFilter

    def get_queryset(self):
        builder = self.request.user
        return Deficiency.objects.filter(home_inspection__inspection__builder=builder)

    def get_serializer_class(self):
        serializer_class = super().get_serializer_class()

        if self.request.method == "GET":
            if not self.kwargs.get("pk"):
                serializer_class = builder.DeficiencyListSerializer

        return serializer_class


class DefImageDeleteView(generics.DestroyAPIView):
    serializer_class = builder.DefImageSerializer
    permission_class = (IsAuthenticated, IsBuilder)
    queryset = DefImage.objects.all()

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(deficiency__inspection__builder=self.request.user)
        )


class BuilderTradeDeficiencyListView(generics.ListAPIView):
    serializer_class = builder.DeficiencyListSerializer
    permission_classes = (IsAuthenticated, IsBuilder)

    queryset = Deficiency.objects.all()

    def get_queryset(self):
        trade_id = self.kwargs.get("trade_id")
        trade_user = get_object_or_404(User, id=trade_id)

        # Check if the builder is retrieving it's own trade's deficiencies
        if trade_user.user_type == "trade":
            if trade_user.trade.builder.user == self.request.user:
                return super().get_queryset().filter(trade=trade_user)

        return Deficiency.objects.none()


class InspectionReviewCreateView(generics.CreateAPIView):
    serializer_class = builder.InspectionReviewSerializer
    permission_class = (IsAuthenticated, IsBuilder)
    queryset = HomeInspectionReview.objects.all()


class SendDeficiencyEmailView(APIView):
    serializer_class = builder.DeficiencyEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            deficiency_ids = serializer.validated_data["deficiency_ids"]
            deficiencies = Deficiency.objects.filter(id__in=deficiency_ids)

            # Calculate outstanding days for each deficiency
            for deficiency in deficiencies:
                deficiency.outstanding_days = (
                    date.today() - deficiency.created_at
                ).days

            # Render the email template with context
            email_content = render_to_string(
                "deficiency_email.html", {"deficiencies": deficiencies}
            )

            msg = EmailMultiAlternatives("Deficiency Report", "", EMAIL_HOST, [email])
            msg.attach_alternative(email_content, "text/html")
            msg.send()

            return Response({"status": "success"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
