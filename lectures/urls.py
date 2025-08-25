from django.urls import path, include
from rest_framework_nested import routers
from common.router.routers import router
from .views import LectureViewSet, HomeworkAssignmentViewSet


app_name = "lectures"

lectures_router = routers.NestedSimpleRouter(router, r"courses", lookup="course")
lectures_router.register(r"lectures", LectureViewSet, basename="course-lectures")


assignments_router = routers.NestedSimpleRouter(
    lectures_router, r"lectures", lookup="lecture"
)
assignments_router.register(
    r"assignments", HomeworkAssignmentViewSet, basename="lecture-assignments"
)


urlpatterns = [
    path("", include(lectures_router.urls)),
    path("", include(assignments_router.urls)),
]
