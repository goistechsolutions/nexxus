import logging
import time
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("nexxus.request")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-Id", str(uuid4()))
        trace_id = request.headers.get("X-Trace-Id", str(uuid4()))
        request.state.request_id = request_id
        request.state.trace_id = trace_id
        started = time.perf_counter()
        response = await call_next(request)
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        logger.info(
            "request_completed",
            extra={
                "request_id": request_id,
                "trace_id": trace_id,
                "tenant_id": request.headers.get("X-Tenant-Id"),
                "user_id": request.headers.get("X-User-Id"),
                "analysis_id": request.headers.get("X-Analysis-Id"),
                "latency_ms": latency_ms,
                "status_code": response.status_code,
            },
        )
        response.headers["X-Request-Id"] = request_id
        response.headers["X-Trace-Id"] = trace_id
        response.headers["X-Response-Time-Ms"] = str(latency_ms)
        return response
