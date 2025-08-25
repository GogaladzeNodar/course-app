from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from lectures.models import Lecture, HomeworkAssignment
from lectures.serializers import LectureSerializer, HomeworkAssignmentSerializer
from common.Permissions.student_and_teacher_permissions import (
    IsEnrolledStudentOrCourseTeacher,
)
from common.Permissions.teacherpermissions import IsCourseTeacher


class LectureViewSet(viewsets.ModelViewSet):
    serializer_class = LectureSerializer

    def get_queryset(self):
        course_pk = self.kwargs.get("course_pk")
        if not course_pk:
            return Lecture.objects.none()

        return Lecture.objects.filter(course_id=course_pk)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = [IsEnrolledStudentOrCourseTeacher]
        else:
            self.permission_classes = [IsCourseTeacher]
        return super().get_permissions()

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, *args, **kwargs):
        """
        Publishes the lecture, making it visible to students.
        """
        lecture = self.get_object()
        if lecture.is_published:
            return Response(
                {"detail": "Lecture is already published."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        lecture.is_published = True
        lecture.save()
        serializer = self.get_serializer(lecture)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="unpublish")
    def unpublish(self, request, *args, **kwargs):
        """
        Unpublishes the lecture, hiding it from students.
        """
        lecture = self.get_object()
        if not lecture.is_published:
            return Response(
                {"detail": "Lecture is already unpublished."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        lecture.is_published = False
        lecture.save()
        serializer = self.get_serializer(lecture)
        return Response(serializer.data)


class HomeworkAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = HomeworkAssignmentSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = [IsEnrolledStudentOrCourseTeacher]
        else:
            self.permission_classes = [IsCourseTeacher]
        return super().get_permissions()

    def get_queryset(self):
        lecture_pk = self.kwargs.get("lecture_pk")
        if not lecture_pk:
            return HomeworkAssignment.objects.none()

        return HomeworkAssignment.objects.filter(lecture_id=lecture_pk)
