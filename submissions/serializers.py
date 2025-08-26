from rest_framework import serializers
from .models import Submission, SubmissionAttachment, Grade, GradeComment
from users.serializers import UserSerializer


class SubmissionAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionAttachment
        fields = ["id", "file", "uploaded_at"]
        read_only_fields = ["uploaded_at"]


class SubmissionSerializer(serializers.ModelSerializer):
    attachments = SubmissionAttachmentSerializer(many=True, read_only=True)
    student = UserSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = [
            "id",
            "assignment",
            "student",
            "submission_number",
            "text",
            "status",
            "submitted_at",
            "updated_at",
            "attachments",
        ]
        read_only_fields = ["status", "submitted_at", "updated_at"]


class GradeCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = GradeComment
        fields = ["id", "grade", "author", "message", "created_at", "updated_at"]
        read_only_fields = ["grade", "author", "created_at", "updated_at"]


class GradeSerializer(serializers.ModelSerializer):
    comments = GradeCommentSerializer(many=True, read_only=True)
    submission = SubmissionSerializer(read_only=True)
    graded_by = UserSerializer(read_only=True)

    class Meta:
        model = Grade
        fields = [
            "id",
            "submission",
            "score",
            "grade_letter",
            "feedback",
            "graded_by",
            "graded_at",
            "updated_at",
            "comments",
        ]
        read_only_fields = ["graded_by", "graded_at", "updated_at"]

    def validate(self, data):
        if "score" in data and data["score"] is not None:
            score = data["score"]
            if score >= 90:
                data["grade_letter"] = Grade.GradeLetter.A
            elif score >= 80:
                data["grade_letter"] = Grade.GradeLetter.B
            elif score >= 70:
                data["grade_letter"] = Grade.GradeLetter.C
            elif score >= 60:
                data["grade_letter"] = Grade.GradeLetter.D
            else:
                data["grade_letter"] = Grade.GradeLetter.F
        elif "score" in data and data["score"] is None:
            data["grade_letter"] = Grade.GradeLetter.NA
        return data
