from django.urls import path, include
from common.router.routers import router
from .views import CourseViewSet

app_name = "courses"


router.register(r"courses", CourseViewSet, basename="course")

urlpatterns = [
    path("", include(router.urls)),
]
