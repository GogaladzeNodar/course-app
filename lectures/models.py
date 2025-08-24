from django.db import models
from courses.models import Course
from django.db.models import UniqueConstraint
from django.contrib.auth import get_user_model

User = get_user_model()


class Lecture(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lectures"
    )
    title = models.CharField(max_length=255)
    # for slug we need generator, which generates a unique slug based on the title
    # (?IN PRESAVE SIGNAL) IN COMMON DIRECTORY TO USE FOR EVERY SLUG FIELD(BLANK=True - WILL BE REQUIRED)
    slug = models.SlugField(max_length=255)
    # topic can be used to categorize lectures within Thematic group.  BUT NOW WE ARE NOT USING IT
    topic = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    presentation = models.FileField(
        upload_to="lectures/presentations/", blank=True, null=True
    )
    order = models.PositiveIntegerField(default=1)
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_lectures"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "lecture"
        verbose_name_plural = "lectures"
        ordering = ["course", "order"]
        indexes = [
            models.Index(fields=["course", "order"]),
        ]

        constraints = [
            UniqueConstraint(
                fields=["course", "slug"], name="unique_lecture_slug_per_course"
            )
        ]

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class HomeworkAssignment(models.Model):
    lecture = models.ForeignKey(
        Lecture, on_delete=models.CASCADE, related_name="homework_assignments"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    max_score = models.PositiveIntegerField(default=100)
    attachment = models.FileField(
        upload_to="assignments/attachments/", blank=True, null=True
    )
    allow_multiple_submissions = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_homework_assignments",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "homework assignment"
        verbose_name_plural = "homework assignments"
        ordering = ["lecture", "due_date"]
        indexes = [
            models.Index(fields=["lecture", "due_date"]),
        ]
        constraints = [
            UniqueConstraint(
                fields=["lecture", "title"],
                name="unique_homework_title_per_lecture",
            )
        ]
