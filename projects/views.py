from rest_framework import generics
from projects.serializers import *
from rest_framework import permissions
from projects.models import Project
from rest_framework import mixins
from rest_framework import viewsets


class ProjectViewset(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    queryset = Project.objects.all()


class ProjectAsigneeUpdateView(generics.RetrieveUpdateAPIView):
    """Projects Assignee view"""

    queryset = Project.objects.all()
    serializer_class = ProjectAssigneeUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == "GET":
            return ProjectAssigneeListSerializer
        else:
            return ProjectAssigneeUpdateSerializer
