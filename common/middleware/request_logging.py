import uuid
import time
from common.logging import logger


class LoguruRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = str(uuid.uuid4())
        request.request_id = request_id
        start_time = time.time()

        # Request start log
        log = logger.bind(
            request_id=request_id, user_id=getattr(request.user, "id", None)
        )
        log.info(
            "Request started",
            event="REQUEST_START",
            method=request.method,
            path=request.path,
        )

        try:
            response = self.get_response(request)
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            log.exception(
                "Request failed",
                event="REQUEST_EXCEPTION",
                method=request.method,
                path=request.path,
                duration_ms=duration_ms,
                error=str(e),
            )
            raise  # Re-raise exception for Django to handle

        # Request end log
        duration_ms = int((time.time() - start_time) * 1000)
        log.info(
            "Request finished",
            event="REQUEST_END",
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        return response
