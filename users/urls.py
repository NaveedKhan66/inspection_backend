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
        "auth/admin/password/",
        views.AdminPasswordResetView.as_view(),
        name="admin-password-reset",
    ),
    path(
        "user/first-login/",
        views.UpdateFirstLoginView.as_view(),
        name="update-first-login",
    ),
    path(
        "user/detail/", views.UpdateUserDetailView.as_view(), name="update-user-detail"
    ),
    path("user/", views.CreateUserView.as_view(), name="create-user"),
    path("user/<str:pk>/", views.UpdateUserView.as_view(), name="update-user"),
    path(
        "auth/user/password/",
        views.SetUserPasswordView.as_view(),
        name="set-user-password",
    ),
]
