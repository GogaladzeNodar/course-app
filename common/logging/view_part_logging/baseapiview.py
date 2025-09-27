from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.views import TokenObtainPairView


class BaseAPIView(APIView):
    """
    Base class for all DRF views.
    Automatically captures request input and stores it in `request.logged_body`.
    """

    def initial(self, request, *args, **kwargs):
        logged_data = {}

        if request.method in ("POST", "PUT", "PATCH") and hasattr(request, "data"):
            logged_data = request.data.copy()
            if "password" in logged_data:
                logged_data["password"] = "***"

        elif request.method == "GET":
            logged_data = request.GET.dict()

        request.logged_body = logged_data

        return super().initial(request, *args, **kwargs)


class BaseViewSet(GenericViewSet, BaseAPIView):
    """
    Base Viewset that captures request input for logging.
    all Viewser inherates from this
    """

    pass


class CustomTokenObtainPairView(BaseAPIView, TokenObtainPairView):
    """
    This is for login view to add logging.
    """

    pass
