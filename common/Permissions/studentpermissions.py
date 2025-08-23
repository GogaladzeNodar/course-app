from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class IsStudent(permissions.BasePermission):
    """
    Custom permission to only allow students to access certain views.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.STUDENT
