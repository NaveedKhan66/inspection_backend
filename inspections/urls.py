from django.urls import path, include
from inspections.views import builder
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"inspection", builder.InspectionViewSet, basename="inspection")


urlpatterns = [
    path(r"builder/", include(router.urls)),
]
