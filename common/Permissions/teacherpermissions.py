from rest_framework import permissions
from django.contrib.auth import get_user_model
from courses.models import CourseTeacher

User = get_user_model()


class IsTeacher(permissions.BasePermission):
    """
    Custom permission to only allow teachers to access certain views.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.TEACHER


class IsCourseOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and request.user.role == User.Role.TEACHER
            and CourseTeacher.objects.filter(
                course=obj, teacher=request.user, role=CourseTeacher.Role.OWNER
            ).exists()
        )


# this permission is used to give students access to course content (every teacher can give access to course content)
class IsCourseTeacher(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and request.user.role == User.Role.TEACHER
            and CourseTeacher.objects.filter(
                course=obj.course, teacher=request.user
            ).exists()
        )
