from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

class CustomAdminPermission(permissions.BasePermission):
    message = "Kindly provide a valid admin account."

    def has_permission(self, request, view):
        is_staff = bool(request.user and request.user.is_staff)
        if not is_staff:
            raise PermissionDenied(self.message)
        return is_staff