from django.apps import AppConfig


class LecturesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "lectures"

    def ready(self):
        from common.signals.slug_signal import auto_generate_slug
        from .models import Lecture

        auto_generate_slug(Lecture, source_field="title", slug_field="slug")
