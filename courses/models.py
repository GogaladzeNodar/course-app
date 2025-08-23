from django.db import models
from django.conf import settings


class Course(models.Model):
    class Visibility(models.TextChoices):
        PUBLIC = "PUBLIC", "Public"
        PRIVATE = "PRIVATE", "Private"

    class EnrollmentType(models.TextChoices):
        INVITE_ONLY = "INVITE_ONLY", "Invite Only"
        OPEN_READONLY = "OPEN_READONLY", "Open Read-only"

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    visibility = models.CharField(
        max_length=50, choices=Visibility.choices, default=Visibility.PRIVATE
    )
    enrollment_type = models.CharField(
        max_length=50,
        choices=EnrollmentType.choices,
        default=EnrollmentType.INVITE_ONLY,
    )

    teachers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="CourseTeacher",
        related_name="taught_courses",
        through_fields=("course", "teacher"),
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_courses",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "course"
        verbose_name_plural = "courses"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["visibility"]),
            models.Index(fields=["created_by"]),
        ]

    def __str__(self):
        return self.title


class CourseTeacher(models.Model):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        CO_TEACHER = "CO_TEACHER", "Co-Teacher"

    course = models.ForeignKey(
        "Course", on_delete=models.CASCADE, related_name="course_teachers"
    )
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=50, choices=Role.choices, default=Role.CO_TEACHER
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="added_teachers",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "teacher of course"
        verbose_name_plural = "teachers of courses"
        unique_together = (
            "course",
            "teacher",
        )
        indexes = [
            models.Index(fields=["course", "teacher"]),
        ]

    def __str__(self):
        return f"{self.teacher.firstname} {self.teacher.lastname} - {self.role} in {self.course.title}"


class Enrollment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"

    course = models.ForeignKey(
        "Course", on_delete=models.CASCADE, related_name="enrollments"
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrolled_courses",
    )

    status = models.CharField(
        max_length=50, choices=Status.choices, default=Status.PENDING
    )
    is_active = models.BooleanField(default=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="enrollments_added",
    )

    joined_at = models.DateTimeField(auto_now_add=True)
    removed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "enrollment"
        verbose_name_plural = "enrollments"
        unique_together = (
            "course",
            "student",
        )
        indexes = [
            models.Index(fields=["student", "is_active"]),
            models.Index(fields=["course", "is_active"]),
        ]

    def __str__(self):
        return f"{self.student.firstname} {self.student.lastname} - {self.status} in {self.course.title}"
