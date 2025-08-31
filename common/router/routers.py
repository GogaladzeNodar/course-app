from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

#  Base router
from courses.views import CourseViewSet
from lectures.views import LectureViewSet, HomeworkAssignmentViewSet
from submissions.views import SubmissionViewSet, GradeViewSet, GradeCommentViewSet

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")

# Nested: lectures under courses
lectures_router = routers.NestedSimpleRouter(router, r"courses", lookup="course")
lectures_router.register(r"lectures", LectureViewSet, basename="course-lectures")

# Nested: assignments under lectures
assignments_router = routers.NestedSimpleRouter(lectures_router, r"lectures", lookup="lecture")
assignments_router.register(r"assignments", HomeworkAssignmentViewSet, basename="lecture-assignments")

#  Nested: submissions under assignments
submissions_router = routers.NestedSimpleRouter(assignments_router, r"assignments", lookup="assignment")
submissions_router.register(r"submissions", SubmissionViewSet, basename="assignment-submissions")

#  Nested: grades under submissions
grades_router = routers.NestedSimpleRouter(submissions_router, r"submissions", lookup="submission")
grades_router.register(r"grades", GradeViewSet, basename="submission-grades")

# Nested: comments under grades
comments_router = routers.NestedSimpleRouter(grades_router, r"grades", lookup="grade")
comments_router.register(r"comments", GradeCommentViewSet, basename="grade-comments")
