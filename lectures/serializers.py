from rest_framework import serializers
from lectures.models import Lecture, HomeworkAssignment
from django.utils.text import slugify


class LectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        exclude = ["topic"]
        read_only_fields = ["id", "created_by", "created_at", "updated_at", "slug"]
        extra_kwargs = {
            "presentation": {"required": False},
            "course": {"write_only": True},
        }

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class HomeworkAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeworkAssignment
        fields = "__all__"
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]
        extra_kwargs = {
            "attachment": {"required": False},
            "lecture": {"write_only": True},
        }

    def create(self, validated_data):

        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)
