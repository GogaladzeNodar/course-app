from rest_framework import permissions
from django.contrib.auth import get_user_model
from courses.models import Enrollment

User = get_user_model()


class IsStudent(permissions.BasePermission):
    """
    Custom permission to only allow students to access certain views.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.STUDENT


class IsEnrolledStudent(permissions.BasePermission):
    """
    Allows access only to an enrolled student of the course.
    """

    def has_permission(self, request, view):
        course_id = view.kwargs.get("course_pk")
        if not course_id:
            return False

        return Enrollment.objects.filter(
            course_id=course_id, student=request.user, is_active=True
        ).exists()
