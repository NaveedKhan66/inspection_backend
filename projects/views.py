from rest_framework import generics
from projects.serializers import *
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

# TODO: Use a different serializer for listing


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
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticated]

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
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_queryset(self):
        project_id = self.kwargs.get("project_id")
        project = get_object_or_404(Project, id=project_id)
        queryset = Home.objects.filter(project=project)
        return queryset

    def get_serializer_class(self):

        if self.request.method == "GET":
            return HomeListRetrieveSerializer

        return HomeSerializer

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


class BluePrintViewSet(viewsets.ModelViewSet):
    queryset = BluePrint.objects.all()
    serializer_class = BluePrintSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        home_id = self.request.query_params.get("home_id")
        if home_id:
            queryset = queryset.filter(home_id=home_id)
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
