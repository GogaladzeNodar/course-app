import uuid
import time
import traceback
import json
from common.logging import logger
from django.db import connection


class LoguruRequestMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = str(uuid.uuid4())
        request.start_time = time.time()

        if request.method in ("POST", "PUT", "PATCH"):
            data = {}
            if hasattr(request, "data"):
                try:
                    data = request.data.copy()
                except Exception:
                    data = {}
            if not data and hasattr(request, "POST"):
                data = request.POST.copy()
                data.pop("csrfmiddlewaretoken", None)
            if "password" in data:
                data["password"] = "***"
            request.logged_body = data

        response = None
        error = None
        error_type = None
        stacktrace = None

        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            error = str(e)
            error_type = type(e).__name__
            stacktrace = traceback.format_exc()
            raise
        finally:
            duration_ms = int((time.time() - request.start_time) * 1000)
            response_status = (
                f"{response.status_code} - {response.reason_phrase}"
                if response
                else "N/A"
            )
            response_size = (
                len(response.content)
                if response and hasattr(response, "content")
                else 0
            )
            content_type = response.get("Content-Type", None) if response else None

            client_info = {
                "client_ip": request.META.get("REMOTE_ADDR"),
                "user_agent": request.META.get("HTTP_USER_AGENT"),
                "reference": request.META.get("HTTP_REFERER"),
            }
            db_query_metrics = {
                "num_queries": len(connection.queries),
                "total_query_time_ms": sum(
                    float(q["time"]) * 1000 for q in connection.queries
                ),
            }

            log = logger.bind(
                request_id=request.request_id,
                user={
                    "id": getattr(getattr(request, "user", None), "id", None),
                    "username": getattr(
                        getattr(request, "user", None), "username", None
                    ),
                    "is_authenticated": getattr(
                        getattr(request, "user", None), "is_authenticated", False
                    ),
                },
                view=getattr(request, "view_name", "unknown"),
                function=getattr(request, "function_name", "unknown"),
                input=getattr(request, "logged_body", {}),
                duration_ms=duration_ms,
                status_code=response_status,
                response_size=response_size,
                content_type=content_type,
                client_info=client_info,
                db_query_metrics=db_query_metrics,
                error=error,
                error_type=error_type,
                stacktrace=stacktrace,
            )

            log.info(
                "Request finished",
                event="REQUEST",
                method=request.method,
                path=request.path,
                payload=request.logged_body,
            )

    def process_view(self, request, view_func, view_args, view_kwargs):
        request.view_name = f"{view_func.__module__}.{view_func.__name__}"
        request.function_name = f"{view_func.__module__}.{view_func.__qualname__}"
        return None
