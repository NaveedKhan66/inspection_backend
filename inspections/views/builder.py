from inspections.models import (
    Inspection,
    Deficiency,
    DefImage,
    HomeInspectionReview,
    HomeInspection,
    DeficiencyNotification,
)
from rest_framework import viewsets, generics
from users.permissions import IsBuilder
from users.permissions import IsEmployee
from users.models import User
from inspections.serializers import builder
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import date
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from inspection_backend.settings import EMAIL_HOST_USER
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from inspections.filters import DeficiencyFilter
from projects.models import Home
from rest_framework.views import APIView
from projects.models import Project
from users.models import Trade
from users.permissions import IsTrade
from users.permissions import IsEmployee
from django.http import Http404


class InspectionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsBuilder | IsAdminUser | IsEmployee]
    serializer_class = builder.InspectionSerializer
    queryset = Inspection.objects.all()

    def get_queryset(self):
        if self.request.user.user_type == "admin":
            return self.queryset

        user = None
        if self.request.user.user_type == "builder":
            user = self.request.user
        elif self.request.user.user_type == "employee":
            user = self.request.user.employee.builder.user

        return super().get_queryset().filter(builder=user)

    def perform_create(self, serializer):
        serializer.save(builder=self.request.user)


class DeficiencyViewSet(viewsets.ModelViewSet):
    serializer_class = builder.DeficiencySerializer
    permission_classes = [IsAuthenticated, IsBuilder | IsTrade | IsEmployee]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DeficiencyFilter
    ordering_fields = ["id"]
    ordering = ["-id"]

    # TODO: add permission for admin to list deficiencies.
    def filter_queryset(self, queryset):
        queryset = super(DeficiencyViewSet, self).filter_queryset(queryset)
        return queryset.order_by("-id")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["view"] = self
        return context

    def get_queryset(self):
        user = self.request.user
        if user.user_type == "builder" or user.user_type == "employee":

            if user.user_type == "employee":
                user = user.employee.builder.user

            return Deficiency.objects.filter(home_inspection__inspection__builder=user)
        elif user.user_type == "trade":
            return Deficiency.objects.filter(trade=user)
        else:
            return Deficiency.objects.none()

    def get_serializer_class(self):
        serializer_class = super().get_serializer_class()

        if self.request.method == "GET":
            if not self.kwargs.get("pk"):
                serializer_class = builder.DeficiencyListSerializer

        return serializer_class

    def retrieve(self, request, *args, **kwargs):
        # Apply filters even in retrieve
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

        try:
            instance = queryset.get(**filter_kwargs)
        except Deficiency.DoesNotExist:
            raise Http404

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        inspection = instance.home_inspection.inspection
        response = super().destroy(request, *args, **kwargs)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            inspection.no_of_def -= 1
            inspection.save()
        return response


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
    permission_classes = (IsAuthenticated, IsBuilder | IsEmployee)

    queryset = Deficiency.objects.all()

    def get_queryset(self):
        trade_id = self.kwargs.get("trade_id")
        trade_user = get_object_or_404(User, id=trade_id)

        # Check if the builder is retrieving it's own trade's deficiencies
        user = None

        if self.request.user.user_type == "builder":
            user = self.request.user
        elif self.request.user.user_type == "employee":
            user = self.request.user.employee.builder.user

        if trade_user.user_type == "trade":
            if trade_user.trade.builder.user == user:
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
            due_date = str(serializer.validated_data["due_date"])
            deficiencies = Deficiency.objects.filter(id__in=deficiency_ids)
            user = self.request.user
            username = user.first_name + " " + user.last_name
            inspection_name = "Deficiency Report"
            if deficiencies.exists():
                inspection_name = deficiencies.first().home_inspection.inspection.name

            # Render the email template with context
            email_content = render_to_string(
                "deficiency_email.html",
                {
                    "deficiencies": deficiencies,
                    "inspection_name": inspection_name,
                    "username": username,
                    "due_date": due_date,
                },
            )

            msg = EmailMultiAlternatives(
                due_date + " - " + inspection_name, "", EMAIL_HOST_USER, [email]
            )
            msg.attach_alternative(email_content, "text/html")
            msg.send()

            return Response({"status": "success"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HomeInspectionListView(generics.ListAPIView):
    serializer_class = builder.HomeInspectionListSerializer
    permission_classes = [IsAuthenticated, IsBuilder | IsAdminUser | IsEmployee]
    queryset = HomeInspection.objects.all()

    def get_queryset(self):
        home_id = self.kwargs.get("home_id")
        home = get_object_or_404(Home, id=home_id)
        return super().get_queryset().filter(home=home)


class TotalDeficiencies(APIView):

    permission_classes = [IsAuthenticated, IsBuilder | IsEmployee]

    def get(self, request, *args, **kwargs):
        builder = None
        if request.user.user_type == "builder":
            builder = request.user
        elif request.user.user_type == "employee":
            builder = request.user.employee.builder.user

        deficiencies = Deficiency.objects.select_related("home_inspection").filter(
            home_inspection__inspection__builder=builder
        )
        total_deficiencies = deficiencies.count()
        complete_deficiencies = deficiencies.filter(status="complete").count()
        incomplete_deficiencies = total_deficiencies - complete_deficiencies

        response_data = {
            "total_deficiencies": total_deficiencies,
            "complete_deficiencies": complete_deficiencies,
            "incomplete_deficiencies": incomplete_deficiencies,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class ProjectTotalDeficiencies(APIView):

    permission_classes = [IsAuthenticated, IsBuilder | IsEmployee]

    def get(self, request, *args, **kwargs):
        user = None

        if request.user.user_type == "builder":
            user = request.user
        elif request.user.user_type == "employee":
            user = request.user.employee.builder.user

        # Get all projects where the builder is the current user
        projects = Project.objects.filter(builder=user)
        project_data = []

        for project in projects:
            # Get all homes in the current project
            homes = project.homes.all()
            home_ids = homes.values_list("id", flat=True)

            # Get all deficiencies for these homes
            deficiencies = Deficiency.objects.select_related("home_inspection").filter(
                home_inspection__home__in=home_ids
            )
            total_deficiencies = deficiencies.count()
            complete_deficiencies = deficiencies.filter(status="complete").count()
            incomplete_deficiencies = total_deficiencies - complete_deficiencies

            project_data.append(
                {
                    "id": project.id,
                    "name": project.name,
                    "total_deficiencies": total_deficiencies,
                    "complete_deficiencies": complete_deficiencies,
                    "incomplete_deficiencies": incomplete_deficiencies,
                }
            )

        return Response(project_data, status=status.HTTP_200_OK)


class DeficiencyFilterView(APIView):
    permission_classes = [IsAuthenticated, IsBuilder | IsEmployee]

    def get(self, request, *args, **kwargs):
        builder = request.user
        if request.user.user_type == "employee":
            builder = request.user.employee.builder.user

        inspection = request.query_params.get("inspection")
        trade_name = request.query_params.get("trade")

        builder_deficiencies = Deficiency.objects.select_related(
            "home_inspection"
        ).filter(home_inspection__inspection__builder=builder)
        deficiencies = None

        if inspection and trade_name:
            deficiencies = builder_deficiencies.filter(
                home_inspection__inspection__name=inspection,
                trade__first_name__contains=trade_name,
            )

        elif inspection:
            deficiencies = builder_deficiencies.filter(
                home_inspection__inspection__name=inspection
            )
        elif trade_name:
            deficiencies = builder_deficiencies.filter(
                trade__first_name__contains=trade_name
            )
        else:
            deficiencies = builder_deficiencies

        total_deficiencies = deficiencies.count()
        complete_deficiencies = deficiencies.filter(status="complete").count()
        incomplete_deficiencies = total_deficiencies - complete_deficiencies
        response_data = {
            "total_deficiencies": total_deficiencies,
            "complete_deficiencies": complete_deficiencies,
            "incomplete_deficiencies": incomplete_deficiencies,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class DeficiencyInspectionFilterView(APIView):

    permission_classes = [IsAuthenticated, IsBuilder | IsEmployee]

    def get(self, request, *args, **kwargs):
        builder = None

        if self.request.user.user_type == "builder":
            builder = self.request.user
        elif self.request.user.user_type == "employee":
            builder = self.request.user.employee.builder.user

        inspection = request.query_params.get("inspection")
        deficiencies = None
        if inspection:
            deficiencies = Deficiency.objects.select_related("home_inspection").filter(
                home_inspection__inspection__name=inspection,
                home_inspection__inspection__builder=builder,
            )
        else:
            deficiencies = Deficiency.objects.select_related("home_inspection").filter(
                home_inspection__inspection__builder=builder
            )
        trades = Trade.objects.filter(builder=builder.builder)
        response_data = []

        for trade in trades:
            total_deficiencies = deficiencies.count()
            complete_deficiencies = deficiencies.filter(
                trade=trade.user, status="complete"
            ).count()
            incomplete_deficiencies = total_deficiencies - complete_deficiencies
            incomplete_deficiencies_pct = 0
            if total_deficiencies > 0:
                incomplete_deficiencies_pct = (
                    incomplete_deficiencies / total_deficiencies
                ) * 100
            response_data.append(
                {
                    "trade": trade.user.get_full_name(),
                    "incomplete_percentage": int(incomplete_deficiencies_pct),
                }
            )

        return Response(response_data, status=status.HTTP_200_OK)


class DeficienciesFilterOptionsView(APIView):
    """
    Get filter options based on status, trades and locations.
    These filters will be used to filter deficiencies
    """

    permission_classes = [IsAuthenticated, IsBuilder | IsEmployee | IsTrade]

    def get(self, request, *args, **kwargs):
        builder = None
        locations = None
        trades = None
        if self.request.user.user_type != "trade":
            if self.request.user.user_type == "builder":
                builder = self.request.user
            elif self.request.user.user_type == "employee":
                builder = self.request.user.employee.builder.user
            trades = User.objects.filter(trade__builder=builder.builder)
            trade_values = trades.distinct().values("id", "first_name", "last_name")

            # Get unique locations
            locations = (
                Deficiency.objects.exclude(trade__in=trades, location__isnull=True)
                .values_list("location", flat=True)
                .distinct()
            )
        locations = (
            Deficiency.objects.filter(trade=self.request.user, location__isnull=False)
            .values_list("location", flat=True)
            .distinct()
        )
        # Get status types
        status_types = [
            {"value": status[0], "label": status[1]}
            for status in Deficiency.STATUS_TYPES
        ]

        return Response(
            {
                "trades": list(trade_values),
                "status_types": status_types,
                "locations": list(locations),
            }
        )


class DeficiencyNotificationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsBuilder | IsEmployee | IsTrade]
    queryset = DeficiencyNotification.objects.filter(read=False)
    serializer_class = builder.DeficiencyNotificationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user).order_by("-id")


class DeficiencyNotificationReadView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsBuilder | IsEmployee | IsTrade]
    queryset = DeficiencyNotification.objects.all()
    serializer_class = builder.DeficiencyNotificationReadSerializer


class DeficiencyNotificationAllReadView(APIView):
    permission_classes = [IsAuthenticated, IsBuilder | IsEmployee | IsTrade]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        notifications = DeficiencyNotification.objects.filter(user=user)
        notifications.update(read=True)
        return Response(status=status.HTTP_200_OK)
