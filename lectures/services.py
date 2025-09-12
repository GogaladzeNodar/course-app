from .models import Lecture, HomeworkAssignment
from django.db import models
from django.utils.text import slugify


class LectureService:
    @staticmethod
    def reorder(lecture, new_order):
        course = lecture.course
        lectures = course.lectures.exclude(id=lecture.id).order_by("order")

        new_order = min(new_order, lectures.count())
        lectures = list(lectures.exclude(id=lecture.id))
        lectures.insert(new_order - 1, lecture)
        for idx, l in enumerate(lectures, start=1):
            if l.order != idx:
                l.order = idx
                l.save(update_fields=["order"])
