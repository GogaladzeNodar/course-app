from rest_framework_nested import routers
from django.urls import path, include
from lectures.urls import assignments_router


from .views import SubmissionViewSet, GradeViewSet, GradeCommentViewSet

app_name = "submissions"


submissions_router = routers.NestedSimpleRouter(
    assignments_router, r"assignments", lookup="assignment"
)
submissions_router.register(
    r"submissions", SubmissionViewSet, basename="assignment-submissions"
)


grades_router = routers.NestedSimpleRouter(
    submissions_router, r"submissions", lookup="submission"
)
grades_router.register(r"grades", GradeViewSet, basename="submission-grades")


comments_router = routers.NestedSimpleRouter(grades_router, r"grades", lookup="grade")
comments_router.register(r"comments", GradeCommentViewSet, basename="grade-comments")

urlpatterns = [
    path("", include(submissions_router.urls)),
    path("", include(grades_router.urls)),
    path("", include(comments_router.urls)),
]
