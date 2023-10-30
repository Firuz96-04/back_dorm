from rest_framework import permissions


class CommandantPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        print(bool(request.user.is_authenticated and request.user.role == "3"), 'req')
        return bool(request.user.is_authenticated)
