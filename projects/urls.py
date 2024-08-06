"""inspection_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from projects.views import admin, builder
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"project", admin.ProjectViewset, basename="project")

home_router = DefaultRouter()
home_router.register(r"home", admin.HomeViewSet, basename="home")

blue_print_router = DefaultRouter()
blue_print_router.register(r"blueprint", admin.BluePrintViewSet, basename="blueprint")

builder_project_router = DefaultRouter()
builder_project_router.register(
    r"builder/project",
    builder.BuilderProjectListRetrieveView,
    basename="builder-project",
)


urlpatterns = [
    path(r"", include(router.urls)),
    path(r"project/<uuid:project_id>/", include(home_router.urls)),
    path(r"home/<uuid:home_id>/", include(blue_print_router.urls)),
    path(
        "project/<pk>/assignee/",
        admin.ProjectAsigneeUpdateView.as_view(),
        name="project-assignee",
    ),
    path(
        "home/blueprint/image/<int:pk>",
        admin.BluePrintImageDelete.as_view(),
        name="blueprint-image-delete",
    ),
    path(
        "builder/<uuid:builder_id>/projects/",
        admin.BuilderProjectListView.as_view(),
        name="builder-project-list",
    ),
    path("dashboard/", admin.DashboardAPIView.as_view(), name="dashboard-api"),
    path("home-dashboard/", admin.HomeDashboard.as_view(), name="home-dashboard"),
    path(r"", include(builder_project_router.urls)),
]
