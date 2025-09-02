from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Submission, SubmissionAttachment, Grade, GradeComment
from lectures.models import HomeworkAssignment
from .services import SubmissionService, GradeService
from .serializers import (
    SubmissionSerializer,
    SubmissionAttachmentSerializer,
    GradeSerializer,
    GradeCommentSerializer,
)

from common.Permissions.student_and_teacher_permissions import (
    IsSubmissionOwnerOrCourseTeacher,
    IsCommentAuthor,
)
from common.Permissions.studentpermissions import IsStudent, IsEnrolledStudent
from common.Permissions.teacherpermissions import IsCourseTeacher, IsTeacher


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

    def get_permissions(self):
        if self.action in ["create"]:
            self.permission_classes = [IsAuthenticated, IsStudent, IsEnrolledStudent]
        elif self.action in ["retrieve"]:
            self.permission_classes = [
                IsAuthenticated,
                IsSubmissionOwnerOrCourseTeacher,
            ]
        elif self.action in ["list"]:
            self.permission_classes = [IsAuthenticated, IsCourseTeacher]
        elif self.action in ["destroy"]:
            self.permission_classes = [
                IsAuthenticated,
                IsSubmissionOwnerOrCourseTeacher,
            ]
        elif self.action in ["update", "partial_update"]:
            self.permission_classes = [
                IsAuthenticated,
                IsCourseTeacher,
            ]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if user.is_authenticated:
            if user.role == user.Role.STUDENT:
                return queryset.filter(student=user)
            elif user.role == user.Role.TEACHER:
                return queryset.filter(
                    assignment__lecture__course__courseteacher__teacher=user
                ).distinct()  # avoid duplicates if multiple roles()

        return queryset.none()

    def perform_create(self, serializer):
        assignment_id = self.kwargs.get("assignment_pk")
        assignment = get_object_or_404(HomeworkAssignment, pk=assignment_id)
        submission = SubmissionService.create_submission(
            assignment=assignment,
            student=self.request.user,
            text=serializer.validated_data.get("text", ""),
        )
        serializer.instance = submission


class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsTeacher, IsCourseTeacher]
        elif self.action in ["retrieve"]:
            self.permission_classes = [
                IsAuthenticated,
                IsSubmissionOwnerOrCourseTeacher,
            ]
        elif self.action in ["list"]:
            self.permission_classes = [
                IsAuthenticated,
                IsSubmissionOwnerOrCourseTeacher,
            ]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()  # Grade.objects.all()

        if not user.is_authenticated:
            return queryset.none()

        assignment_id = self.kwargs.get("assignment_pk")

        if user.role == user.Role.TEACHER:
            return queryset.filter(
                submission__assignment_id=assignment_id,
                submission__assignment__lecture__course__coursedteacher__teacher=user,
            )

        if user.role == user.Role.STUDENT:
            return queryset.filter(
                submission__assignment_id=assignment_id, submission__student=user
            )

        return queryset.none()

    def perform_create(self, serializer):
        submission_id = self.kwargs.get("submission_pk")
        submission = get_object_or_404(Submission, pk=submission_id)
        grade = GradeService.create_or_update_grade(
            submission=submission,
            score=serializer.validated_data.get("score"),
            feedback=serializer.validated_data.get("feedback", ""),
            graded_by=self.request.user,
        )
        serializer.instance = grade

    def perform_update(self, serializer):
        submission_id = self.kwargs.get("submission_pk")
        submission = get_object_or_404(Submission, pk=submission_id)
        grade = GradeService.create_or_update_grade(
            submission=submission,
            score=serializer.validated_data.get("score"),
            feedback=serializer.validated_data.get("feedback", ""),
            graded_by=self.request.user,
        )
        serializer.instance = grade


class GradeCommentViewSet(viewsets.ModelViewSet):
    queryset = GradeComment.objects.all()
    serializer_class = GradeCommentSerializer

    def get_queryset(self):
        user = self.request.user
        grade_id = self.kwargs.get("grade_pk")
        if not user.is_authenticated:
            return GradeComment.objects.none()

        queryset = GradeComment.objects.filter(grade_id=grade_id)

        if user.role == user.Role.TEACHER:
            queryset = queryset.filter(
                grade__assignment__lecture__course__coursedteacher__teacher=user
            )
        elif user.role == user.Role.STUDENT:
            queryset = queryset.filter(grade__student=user)

        return queryset

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsCommentAuthor]
        return super().get_permissions()

    def perform_create(self, serializer):
        grade_id = self.kwargs.get("grade_pk")
        grade = get_object_or_404(Grade, pk=grade_id)
        serializer.save(author=self.request.user, grade=grade)
