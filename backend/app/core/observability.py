import logging
import re
import time
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import get_settings
from app.core.logging import request_id_var, trace_id_var

logger = logging.getLogger("nexxus.request")

_SAFE_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,128}$")


def _safe_correlation_id(value: str | None) -> str:
    if value and _SAFE_ID_PATTERN.fullmatch(value):
        return value
    return str(uuid4())


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:
        request_id = _safe_correlation_id(request.headers.get("X-Request-Id"))
        trace_id = _safe_correlation_id(request.headers.get("X-Trace-Id"))

        request.state.request_id = request_id
        request.state.trace_id = trace_id

        request_token = request_id_var.set(request_id)
        trace_token = trace_id_var.set(trace_id)

        settings = get_settings()
        started = time.perf_counter()

        try:
            response = await call_next(request)
            latency_ms = round((time.perf_counter() - started) * 1000, 2)

            logger.info(
                "request_completed",
                extra={
                    "environment": settings.environment,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "latency_ms": latency_ms,
                },
            )

            response.headers["X-Request-Id"] = request_id
            response.headers["X-Trace-Id"] = trace_id
            response.headers["X-Response-Time-Ms"] = str(latency_ms)
            return response
        except Exception:
            latency_ms = round((time.perf_counter() - started) * 1000, 2)

            logger.exception(
                "request_failed",
                extra={
                    "environment": settings.environment,
                    "method": request.method,
                    "path": request.url.path,
                    "latency_ms": latency_ms,
                },
            )
            raise
        finally:
            request_id_var.reset(request_token)
            trace_id_var.reset(trace_token)
