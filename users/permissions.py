from rest_framework import permissions


class IsBuilder(permissions.IsAuthenticated):

    def has_permission(self, request, view):
        return request.user.user_type == "builder"
