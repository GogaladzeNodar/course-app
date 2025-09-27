from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Course, Enrollment, CourseTeacher
from .serializers import (
    CourseSerializer,
    CourseTeacherCreateSerializer,
    EnrollmentCreateSerializer,
    EnrollmentUpdateSerializer,
    CourseTeacherSerializer,
    EnrollmentSerializer,
)
from common.Permissions.studentpermissions import IsStudent
from common.Permissions.teacherpermissions import (
    IsTeacher,
    IsCourseOwner,
    IsCourseTeacher,
)
from django.db import IntegrityError
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.contrib.auth import get_user_model
from common.logging.view_part_logging.baseapiview import BaseViewSet
User = get_user_model()


class CourseViewSet(BaseViewSet, viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ["create"]:
            self.permission_classes = [IsAuthenticated, IsTeacher]
        elif self.action in [
            "update",
            "partial_update",
            "destroy",
            "add_teacher",
            "enroll_student",
        ]:
            self.permission_classes = [IsAuthenticated, IsCourseOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        course = serializer.save(created_by=self.request.user)
        CourseTeacher.objects.create(
            course=course,
            teacher=self.request.user,
            role=CourseTeacher.Role.OWNER,
            added_by=self.request.user,
        )

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Course.objects.filter(visibility=Course.Visibility.PUBLIC)

        if user.role == User.Role.TEACHER:
            return Course.objects.filter(
                teachers__teacher=user
            ) | Course.objects.filter(visibility=Course.Visibility.PUBLIC)

        if user.role == User.Role.STUDENT:
            return Course.objects.filter(
                enrollments__student=user, enrollments__is_active=True
            ) | Course.objects.filter(visibility=Course.Visibility.PUBLIC)

        return Course.objects.none()

    @action(detail=True, methods=["Post"], url_path="add-teacher")
    def add_teacher(self, request, pk=None):
        course = self.get_object()
        serializer = CourseTeacherCreateSerializer(
            data=request.data, context={"request": request, "course": course}
        )
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Teacher added successfully."}, status=201)
        except (ValidationError, IntegrityError) as e:
            return Response({"error": str(e)}, status=400)

    @action(
        detail=True,
        methods=["post"],
        url_path="enroll-student",
        permission_classes=[IsAuthenticated, IsStudent],
    )
    def enroll_student(self, request, pk=None):
        course = self.get_object()
        serializer = EnrollmentCreateSerializer(
            data=request.data, context={"request": request, "course": course}
        )
        try:
            serializer.is_valid(raise_exception=True)
            enrollment = serializer.save()
            return Response(
                {
                    "message": "Enrollment request sent successfully.",
                    "status": enrollment.status,
                },
                status=201,
            )
        except (ValidationError, IntegrityError) as e:
            return Response({"error": str(e)}, status=400)

    @action(detail=True, methods=["delete"], url_path="teachers/(?P<teacher_id>[^/.]+)")
    def remove_teacher(self, request, pk=None, teacher_id=None):
        course = self.get_object()

        try:
            course_owner_teacher_relation = CourseTeacher.objects.get(
                course=course, teacher=request.user, role=CourseTeacher.Role.OWNER
            )
        except CourseTeacher.DoesNotExist:
            return Response(
                {"error": "Only the course owner can remove teachers."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            teacher_to_remove = User.objects.get(id=teacher_id)
            if course_owner_teacher_relation.teacher == teacher_to_remove:
                return Response(
                    {"error": "Course owner cannot remove themselves."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            course_teacher_relation = CourseTeacher.objects.get(
                course=course, teacher=teacher_to_remove
            )
            course_teacher_relation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response(
                {"error": "Teacher not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except CourseTeacher.DoesNotExist:
            return Response(
                {"error": "Teacher is not part of this course."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["delete"], url_path="students/(?P<student_id>[^/.]+)")
    def remove_student(self, request, pk=None, student_id=None):
        course = self.get_object()
        try:
            student_to_remove = User.objects.get(id=student_id, role=User.Role.STUDENT)
            enrollment = Enrollment.objects.get(
                course=course, student=student_to_remove
            )
            enrollment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response(
                {"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Enrollment.DoesNotExist:
            return Response(
                {"error": "Student is not enrolled in this course."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["get"])
    def teachers(self, request, pk=None):
        course = self.get_object()
        teachers = course.course_teachers.all()
        serializer = CourseTeacherSerializer(teachers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def students(self, request, pk=None):
        course = self.get_object()
        students = course.enrollments.filter(is_active=True)
        serializer = EnrollmentSerializer(students, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["get"],
        url_path="pending-enrollments",
        permission_classes=[IsAuthenticated, IsCourseTeacher],
    )
    def pending_enrollments(self, request, pk=None):
        course = self.get_object()
        enrollments = course.enrollments.filter(status=Enrollment.Status.PENDING)
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["patch"],
        url_path="enrollments/(?P<enrollment_id>[^/.]+)",
        permission_classes=[IsAuthenticated, IsCourseTeacher],
    )
    def update_enrollment_status(self, request, pk=None, enrollment_id=None):
        course = self.get_object()
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id, course=course)
        except Enrollment.DoesNotExist:
            return Response(
                {"error": "Enrollment not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = EnrollmentUpdateSerializer(
            enrollment, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
