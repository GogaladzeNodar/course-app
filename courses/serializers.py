from rest_framework import serializers
from .models import Course, CourseTeacher, Enrollment
from users.serializers import UserSerializer
from django.conf import settings


class CourseTeacherSerializer(serializers.ModelSerializer):
    teacher = UserSerializer(read_only=True)

    class Meta:
        model = CourseTeacher
        fields = ["teacher", "role", "created_at"]


class EnrollmentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ["student", "status", "is_active", "joined_at"]


class CourseSerializer(serializers.ModelSerializer):
    teachers = CourseTeacherSerializer(
        source="course_teachers", many=True, read_only=True
    )
    students = EnrollmentSerializer(source="enrollments", many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "visibility",
            "enrollment_type",
            "created_by",
            "created_at",
            "updated_at",
            "teachers",
            "students",
        ]
        read_only_fields = [
            "created_by",
            "created_at",
            "updated_at",
            "teachers",
            "students",
        ]


class CourseTeacherCreateSerializer(serializers.Serializer):
    """
    Serializer for adding a teacher to a course.
    This serializer expects an email of the teacher to be added.
    It validates that the user exists and is a teacher.
    If the user is not a teacher, it raises a validation error.
    If the user is already a teacher in the course, it raises a validation error.
    """

    email = serializers.EmailField(write_only=True)

    def validate_email(self, value):
        try:
            user = settings.AUTH_USER_MODEL.objects.get(email=value)
            if user.role != settings.AUTH_USER_MODEL.Role.TEACHER:
                raise serializers.ValidationError("User is not a teacher.")
        except settings.AUTH_USER_MODEL.DoesNotExist:
            raise serializers.ValidationError("User does not exist with this email.")
        return value

    def create(self, validated_data):
        email = validated_data.pop("email")
        teacher_user = settings.AUTH_USER_MODEL.objects.get(email=email)
        request_user = self.context.get("request").user
        course = self.context.get("course")

        if course.created_by != request_user:
            raise serializers.ValidationError("Only the course owner can add teachers.")

        if not course:
            raise serializers.ValidationError("Course context is required.")

        if CourseTeacher.objects.filter(course=course, teacher=teacher_user).exists():
            raise serializers.ValidationError(
                "This teacher is already added to the course."
            )

        course_teacher = CourseTeacher.objects.create(
            course=course,
            teacher=teacher_user,
            role=CourseTeacher.Role.CO_TEACHER,  # if he is not creator of course he will be co-teacher all the time
            added_by=self.context.get("request").user,
        )
        return course_teacher


class EnrollmentCreateSerializer(serializers.Serializer):
    class Meta:
        model = Enrollment
        fields = []

    def create(self, validated_data):
        request_user = self.context.get("request").user
        course = self.context.get("course")

        # if only students can enroll, uncomment the following lines, but, let's say teacher can enroll also
        # if request_user.role != settings.AUTH_USER_MODEL.Role.STUDENT:
        #     raise serializers.ValidationError("Only students can enroll in courses.")

        if Enrollment.objects.filter(course=course, student=request_user).exists():
            raise serializers.ValidationError(
                "You are already enrolled in this course."
            )

        if course.enrollment_type == "OPEN_READONLY":
            status = Enrollment.Status.ACCEPTED

        else:
            status = Enrollment.Status.PENDING

        enrollment = Enrollment.objects.create(
            course=course,
            student=request_user,
            status=status,
            is_active=True if status == Enrollment.Status.ACCEPTED else False,
        )
        return enrollment


class EnrollmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ["status"]

    def update(self, instance, validated_data):
        new_status = validated_data.get("status")
        if new_status == "REJECTED":
            instance.is_active = False
            instance.status = new_status
            instance.save()
        elif new_status == "ACCEPTED":
            instance.is_active = True
            instance.status = new_status
            instance.save()
        else:
            raise serializers.ValidationError(
                "Invalid status. Only ACCEPTED or REJECTED are allowed."
            )
        return instance
