from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from users import views

urlpatterns = [
    path(
        "auth/token/",
        views.CustomTokenObtainPairView.as_view(),
        name="token-obtain-pair",
    ),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path(
        "auth/admin/password",
        views.AdminPasswordResetView.as_view(),
        name="admin-password-reset",
    ),
    path(
        "users/first-login/",
        views.UpdateFirstLoginView.as_view(),
        name="update-first-login",
    ),
]
