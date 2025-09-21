import uuid
import time
from common.logging import logger


class LoguruRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Request setup
        request.request_id = str(uuid.uuid4())
        request.start_time = time.time()
        try:
            response = self.get_response(request)
        except Exception as e:
            # log exception
            duration_ms = int((time.time() - request.start_time) * 1000)
            log = logger.bind(
                request_id=getattr(request, "request_id", None),
                user=getattr(request, "user_info", None),
                view=getattr(request, "view_name", "unknown"),
                function=getattr(request, "function_name", "unknown"),
            )
            log.exception(
                "Request failed",
                event="REQUEST",
                method=request.method,
                path=request.path,
                duration_ms=duration_ms,
                error=str(e),
            )
            raise
        else:
            # log finished request
            duration_ms = int((time.time() - request.start_time) * 1000)
            response_size = len(getattr(response, "content", b""))
            content_type = response.get("Content-Type", None)

            log = logger.bind(
                request_id=getattr(request, "request_id", None),
                user=getattr(request, "user_info", None),
                view=getattr(request, "view_name", "unknown"),
                function=getattr(request, "function_name", "unknown"),
            )
            log.info(
                "Request completed",
                event="REQUEST",
                method=request.method,
                path=request.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                response_size=response_size,
                content_type=content_type,
            )
            return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if hasattr(view_func, "cls"):
            function_name = view_func.cls.__name__
        elif hasattr(view_func, "view_class"):
            function_name = view_func.view_class.__name__
        else:
            function_name = getattr(view_func, "__name__", "unknown")

        request.function_name = function_name
        request.view_name = getattr(request.resolver_match, "view_name", "unknown")

        # User info
        user = getattr(request, "user", None)
        request.user_info = {
            "id": getattr(user, "id", None),
            "username": getattr(user, "username", None),
            "is_authenticated": getattr(user, "is_authenticated", False),
        }
