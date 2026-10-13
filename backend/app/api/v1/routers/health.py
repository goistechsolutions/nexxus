from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health/live", summary="Liveness check")
async def live() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "environment": settings.environment}


@router.get("/health/ready", summary="Readiness check")
async def ready() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "environment": settings.environment,
        "checks": {
            "application": "ok"
        },
    }
