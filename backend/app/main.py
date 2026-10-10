from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.observability import RequestContextMiddleware

settings = get_settings()

app = FastAPI(
    title="Nexxus API",
    version="0.1.0",
    openapi_url="/openapi.json",
)
app.add_middleware(RequestContextMiddleware)
app.include_router(api_router, prefix=settings.api_v1_prefix)
