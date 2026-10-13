from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.observability import RequestContextMiddleware

settings = get_settings()
configure_logging()

app = FastAPI(
    title="Nexxus API",
    version="0.1.0",
    openapi_url="/openapi.json" if settings.environment != "prd" else None,
    docs_url="/docs" if settings.environment != "prd" else None,
    redoc_url="/redoc" if settings.environment != "prd" else None,
)

app.add_middleware(RequestContextMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Request-Id",
            "X-Trace-Id",
            "X-Tenant-Id",
            "X-User-Id",
            "X-Analysis-Id",
        ],
    )

app.include_router(api_router, prefix=settings.api_v1_prefix)


def _error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": getattr(request.state, "request_id", None),
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return _error_response(
        request,
        422,
        "validation_error",
        "Request validation failed",
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    return _error_response(
        request,
        exc.status_code,
        "http_error",
        str(exc.detail),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return _error_response(
        request,
        500,
        "internal_error",
        "An unexpected error occurred",
    )
