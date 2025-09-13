from django.apps import AppConfig


class CoursesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "courses"

    def ready(self):
        from common.signals.slug_signal import auto_generate_slug
        from .models import Course

        auto_generate_slug(Course, source_field="title", slug_field="slug")
