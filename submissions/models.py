from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from common.field_validators.advanced_file import AdvancedFileValidator
from lectures.models import HomeworkAssignment
from django.core.validators import MaxValueValidator, MinValueValidator

User = get_user_model()

advanced_validator = AdvancedFileValidator(
    max_size=10 * 1024 * 1024,
    allowed_types=[
        "application/zip",
        "application/pdf",
        "text/plain",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ],
    allowed_inner_types=[
        "application/pdf",
        "text/plain",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ],
)


class Submission(models.Model):
    class SubmissionStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUBMITTED = "SUBMITTED", "Submitted"
        RESUBMITTED = "RESUBMITTED", "Resubmitted"
        LATE = "LATE", "Late"

    assignment = models.ForeignKey(
        HomeworkAssignment, on_delete=models.CASCADE, related_name="submissions"
    )
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="submissions"
    )
    submission_number = models.PositiveIntegerField(default=1)
    text = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.PENDING,
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "submission"
        verbose_name_plural = "submissions"
        ordering = ["-submitted_at"]
        unique_together = (
            "assignment",
            "student",
            "submission_number",
        )  # to allow multiple submissions if enabled
        indexes = [
            models.Index(fields=["assignment", "student"]),
            models.Index(fields=["student", "submitted_at"]),
        ]

    def __str__(self):
        return f"Submission by {self.student.username} for {self.assignement.title}"

    def clean(self):
        if not self.assignment.allow_multiple_submissions:
            existing_submission = (
                Submission.objects.filter(
                    assignment=self.assignment, student=self.student
                )
                .exclude(pk=self.pk)
                .exists()
            )
            if existing_submission:
                raise ValidationError(
                    "You cannot submit more than once for this assignment."
                )
        super().clean()

    def save(self, *args, **kwargs):
        if not self.pk:
            last = (
                Submission.objects.filter(
                    assignement=self.assignement, student=self.student
                )
                .order_by("-submission_number")
                .first()
            )
            self.submission_number = (last.submission_number + 1) if last else 1
        super().save(*args, **kwargs)


class SubmissionAttachment(models.Model):
    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, related_name="attachments"
    )

    file = models.FileField(
        upload_to="submission_attachments/", validators=[advanced_validator]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Attachment for Submission {self.submission.id}"


class Grade(models.Model):

    class GradeLetter(models.TextChoices):
        A = "A", "A"
        B = "B", "B"
        C = "C", "C"
        D = "D", "D"
        F = "F", "F"
        NA = "NA", "Not Applicable"

    submission = models.OneToOneField(
        Submission, on_delete=models.CASCADE, related_name="grade"
    )
    score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True
    )
    grade_letter = models.CharField(
        max_length=5, choices=GradeLetter.choices, default=GradeLetter.NA
    )
    feedback = models.TextField(blank=True, null=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # is_published = models.BooleanField(default=False) # maybe in future
    graded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Grade"
        verbose_name_plural = "Grades"

    def __str__(self):
        return f"Grade for Submission {self.submission.id}"

    def clean(
        self,
    ):  # this validation is not vorking in API so we will handle it in serializer
        # but let it be here for future use in admin panel
        if self.score is None:
            self.grade_letter = self.GradeLetter.NA
        elif self.score >= 90:
            self.grade_letter = self.GradeLetter.A
        elif self.score >= 80:
            self.grade_letter = self.GradeLetter.B
        elif self.score >= 70:
            self.grade_letter = self.GradeLetter.C
        elif self.score >= 60:
            self.grade_letter = self.GradeLetter.D
        else:
            self.grade_letter = self.GradeLetter.F
        super().clean()


class GradeComment(models.Model):

    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.author.first_name} {self.author.last_name}  on Grade {self.grade.id}"
