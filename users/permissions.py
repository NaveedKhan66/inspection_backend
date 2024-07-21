from rest_framework import permissions


class IsBuilder(permissions.IsAuthenticated):

    def has_permission(self, request, view):
        return request.user.user_type == "builder"


class IsEmployee(permissions.IsAuthenticated):

    def has_permission(self, request, view):
        return request.user.user_type == "emplyee"


class IsTrade(permissions.IsAuthenticated):

    def has_permission(self, request, view):
        return request.user.user_type == "trade"


class IsAdminOrReadOnlyForBuilder(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow all actions for admin users
        if request.user and request.user.is_staff:
            return True

        # Allow only read-only actions (GET, HEAD, OPTIONS) for builders
        if request.user and (
            request.user.user_type == "builder" or request.user.user_type == "employee"
        ):
            if view.action in ["list", "retrieve"]:
                return True

        # Deny all other actions
        return False
