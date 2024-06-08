from django.urls import path, re_path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from users.views import admin
from users.views import generic
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r"builder", admin.AdminBuilderViewset, basename="admin-builder")

urlpatterns = [
    re_path(r"user/admin/", include(router.urls)),
    path(
        "auth/token/",
        generic.CustomTokenObtainPairView.as_view(),
        name="token-obtain-pair",
    ),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path(
        "auth/admin/password/",
        admin.AdminPasswordResetView.as_view(),
        name="admin-password-reset",
    ),
    path(
        "user/first-login/",
        generic.UpdateFirstLoginView.as_view(),
        name="update-first-login",
    ),
    path(
        "user/detail/",
        generic.UpdateUserDetailView.as_view(),
        name="update-user-detail",
    ),
    path("user/", generic.CreateUserView.as_view(), name="create-user"),
    path(
        "auth/user/password/",
        generic.SetUserPasswordView.as_view(),
        name="set-user-password",
    ),
]
