from rest_framework import generics
from projects.serializers.admin import *
from rest_framework import permissions
from projects.models import Project
from rest_framework import mixins
from rest_framework import viewsets
from projects.models import Home
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.db.models import Count, Prefetch
from users.models import BuilderEmployee, Builder
from users.permissions import IsAdminOrReadOnlyForBuilder
from inspections.models import HomeInspection
from inspections.models import Deficiency
from users.permissions import IsBuilder
from users.permissions import IsEmployee
from django.contrib.auth import get_user_model
import csv
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from projects.filters import HomeFilter


User = get_user_model()


class ProjectViewset(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    queryset = Project.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ProjectListSerializer
        return ProjectSerializer


class BuilderProjectListView(generics.ListAPIView):
    serializer_class = ProjectListSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_queryset(self):
        builder_id = self.kwargs.get("builder_id")
        builder = get_object_or_404(User, id=builder_id)

        if builder.user_type == "builder":
            queryset = Project.objects.filter(builder=builder)
            return queryset


class ProjectAsigneeUpdateView(generics.RetrieveUpdateAPIView):
    """Projects Assignee view"""

    queryset = Project.objects.all()
    serializer_class = ProjectAssigneeUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == "GET":
            return ProjectAssigneeListSerializer

        return ProjectAssigneeUpdateSerializer


class HomeViewSet(viewsets.ModelViewSet):
    """
    API to
    Create (single and bulk)
    update, retrieve, list home.
    """

    serializer_class = HomeSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnlyForBuilder]
    filter_backends = [DjangoFilterBackend]
    filterset_class = HomeFilter

    def get_queryset(self):
        user = self.request.user
        project = None
        project_id = self.kwargs.get("project_id")

        if user.user_type == "admin":
            project = get_object_or_404(Project, id=project_id)

        elif user.user_type == "builder" or user.user_type == "employee":
            """allow builders to get homes for their own projects"""

            if user.user_type == "employee":
                user = user.employee.builder.user

            project = get_object_or_404(Project, id=project_id, builder=user)

        queryset = Home.objects.filter(project=project).order_by("-updated_at")
        return queryset

    def get_serializer_class(self):
        """
        List: HomeListSerializer
        Retrieve: HomeRetrieveSerializer
        All else: HomeSerializer
        """
        serializer_class = HomeSerializer

        if self.request.method == "GET":
            serializer_class = HomeRetrieveSerializer
            if not self.kwargs.get("pk"):
                serializer_class = HomeListSerializer

        return serializer_class

    def perform_create(self, serializer):
        project_id = self.kwargs.get("project_id")
        project = get_object_or_404(Project, id=project_id)
        serializer.save(project=project)

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)

        if is_many:
            # For bulk creation
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )

        else:
            # For single creation
            return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Reduce no_of_homes count in project when a home is deleted"""

        instance = self.get_object()
        project = instance.project
        response = super().destroy(request, *args, **kwargs)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            if project.no_of_homes > 0:
                project.no_of_homes -= 1
                project.save()
        return response


class BluePrintViewSet(viewsets.ModelViewSet):
    queryset = BluePrint.objects.all()
    serializer_class = BluePrintSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        home_id = self.kwargs.get("home_id")
        if home_id:
            queryset = queryset.filter(home__id=home_id)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class BluePrintImageDelete(generics.DestroyAPIView):
    queryset = BluePrintImage.objects.all()
    serializer_class = BluePrintImageSerializer
    permission_class = (permissions.IsAuthenticated, permissions.IsAdminUser)


class DashboardAPIView(APIView):
    """
    API to provide dashboard statistics for projects.
    """

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        # Query for active, inactive, and hold projects
        active_projects = Project.objects.filter(status="active").count()
        inactive_projects = Project.objects.filter(status="inactive").count()
        hold_projects = Project.objects.filter(status="hold").count()

        # Query for users who are builders with their total projects and employees
        builders_with_projects = (
            User.objects.filter(user_type="builder")
            .annotate(total_projects=Count("projects"))
            .prefetch_related(
                Prefetch(
                    "projects", queryset=Project.objects.only("id", "name", "status")
                ),
                Prefetch(
                    "builder__employees",
                    queryset=BuilderEmployee.objects.select_related("user").only(
                        "user__id", "user__profile_picture"
                    ),
                ),
            )
            .order_by("-total_projects")
        )

        builders_summary = []
        for user in builders_with_projects:
            employees_summary = [
                {
                    "id": employee.user.id,
                    "profile_picture": employee.user.profile_picture,
                    "first_name": employee.user.first_name,
                    "last_name": employee.user.last_name,
                }
                for employee in user.builder.employees.all()
            ]
            builder_data = {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "profile_picture": user.profile_picture,
                "total_projects": user.total_projects,
                "employees": employees_summary,
            }
            builders_summary.append(builder_data)

        response_data = {
            "projects_summary": {
                "active": active_projects,
                "inactive": inactive_projects,
                "hold": hold_projects,
            },
            "builders_summary": builders_summary,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class HomeDashboard(APIView):
    """API to return data for home dashboard"""

    permission_classes = [
        permissions.IsAuthenticated,
        permissions.IsAdminUser | IsBuilder | IsEmployee,
    ]

    def get(self, request, *args, **kwargs):
        total_homes = None
        total_inspections = None
        total_def = None

        set_data = False

        user = None
        if request.user.user_type == "builder":
            user = request.user
        elif request.user.user_type == "employee":
            user = request.user.employee.builder.user
        elif request.user.user_type == "admin":
            builder_id = request.GET.get("builder")

            if not builder_id:
                total_homes = Home.objects.all().count()
                total_inspections = HomeInspection.objects.all().count()
                total_def = Deficiency.objects.all().count()
                set_data = True

            user = get_object_or_404(User, id=builder_id)

        if not set_data:
            total_homes = (
                Home.objects.select_related("project")
                .filter(project__builder=user)
                .count()
            )
            home_inspections = HomeInspection.objects.select_related(
                "inspection"
            ).filter(inspection__builder=user)
            total_inspections = home_inspections.count()

            # Counting deficiencies of selected home inspections to find total deficiencies
            # This is better than retrieving total deficiencies from Deficiency db

            def_count = 0
            for inspection in home_inspections:
                def_count += inspection.deficiencies.count()

            total_def = def_count

        response_data = {
            "total_homes": total_homes,
            "total_inspections": total_inspections,
            "total_deficiencies": total_def,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class GenerateProjectHomesCSV(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, project_id):
        homes = Home.objects.filter(project_id=project_id)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="project_{project_id}_homes.csv"'
        )

        writer = csv.writer(response)
        writer.writerow(
            [
                "Lot No.",
                "Unit/Street No.",
                "Address",
                "Province",
                "City",
                "Postal Code",
                "Enrolment No.",
                "Home Type",
                "Warranty Start Date",
                "Home Owner",
                "Home Owner Email",
                "Home Owner Number",
            ]
        )

        for home in homes:
            writer.writerow(
                [
                    home.lot_no,
                    home.street_no,
                    home.address,
                    home.province,
                    home.city,
                    home.postal_code,
                    home.enrollment_no,
                    home.home_type,
                    home.warranty_start_date,
                    home.owner_name,
                    home.owner_email,
                    home.owner_no,
                ]
            )

        return response
