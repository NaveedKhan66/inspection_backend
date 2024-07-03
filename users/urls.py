from django.urls import path, re_path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from users.views import admin
from users.views import generic
from users.views import builder
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r"builder", admin.AdminBuilderViewset, basename="admin-builder")

builder_trade_router = DefaultRouter()
builder_trade_router.register(
    r"trade", builder.BuilderTradeListView, basename="builder-trade"
)

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
    path(
        "user/admin/builder/<id>/employees/",
        admin.AdminBuilderEmployeeListView.as_view(),
        name="builder-employees-list",
    ),
    path(
        "user/admin/employee/<user__id>",
        admin.AdminBuilderEmployeeRetrieveUpdateDeleteView.as_view(),
        name="builder-employees",
    ),
    path(
        "builder/",
        include(builder_trade_router.urls),
        name="builder-trade-list-retrieve",
    ),
    path(
        "user/<uuid:pk>",
        admin.UserDeleteView.as_view(),
        name="user-delete",
    ),
]
