from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

# May be useful later but not now so commented out
# class CustomAdminPermission(permissions.IsAdminUser):
#     message = "Kindly provide a valid admin account."

#     def has_permission(self, request, view):
#         is_staff = super().has_permission(request, view)
#         if not is_staff:
#             raise PermissionDenied(self.message)
#         return is_staff
