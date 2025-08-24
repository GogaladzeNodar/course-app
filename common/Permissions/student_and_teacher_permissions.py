from courses.models import Course, Enrollment, CourseTeacher
from django.contrib.auth import get_user_model
from rest_framework import permissions
from lectures.models import Lecture

User = get_user_model()


class IsEnrolledStudentOrCourseTeacher(permissions.BasePermission):
    message = "You do not have permission to view this content."

    def _check_permission(self, user, course):
        if not user.is_authenticated:
            return False

        if course.visibility == Course.Visibility.PUBLIC:
            return True

        if user.role == User.Role.TEACHER:
            if CourseTeacher.objects.filter(teacher=user, course=course).exists():
                return True

        if user.role == User.Role.STUDENT:
            if Enrollment.objects.filter(
                student=user, course=course, is_active=True
            ).exists():
                return True

        return False

    def has_permission(self, request, view):
        # This method handles list views (e.g., /courses/{id}/lectures/)
        if not request.method in permissions.SAFE_METHODS:
            return False

        course_id = view.kwargs.get("course_pk")
        if not course_id:
            return False

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return False

        return self._check_permission(request.user, course)

    def has_object_permission(self, request, view, obj):
        # This method handles detail views (e.g., /lectures/{id}/)
        if not request.method in permissions.SAFE_METHODS:
            return False

        course = obj.course
        if not course:
            return False

        return self._check_permission(request.user, course)
