from rest_framework import generics
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework import permissions
from users.permissions import IsBuilder
from projects.models import Project
from projects.serializers.builder import BuilderProjectsListSerializer
from projects.serializers.builder import BuilderProjectsRetrieveSerializer
from rest_framework.viewsets import GenericViewSet


class BuilderProjectListRetrieveView(
    GenericViewSet, ListModelMixin, RetrieveModelMixin
):
    serializer_class = BuilderProjectsListSerializer
    permission_classes = [permissions.IsAuthenticated, IsBuilder]

    queryset = (
        Project.objects.all().select_related("builder").prefetch_related("assignees")
    )

    def get_queryset(self):
        return super().get_queryset().filter(builder=self.request.user)

    def get_serializer_class(self):
        if self.kwargs.get("pk"):
            return BuilderProjectsRetrieveSerializer
        return BuilderProjectsListSerializer
