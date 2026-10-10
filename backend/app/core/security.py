from collections.abc import Callable
from enum import StrEnum

from fastapi import Depends, HTTPException, status


class Scope(StrEnum):
    PLATFORM = "PLATFORM"
    TENANT = "TENANT"
    COMPANY = "COMPANY"


class RoleName(StrEnum):
    PLATFORM_ADMIN = "platform_admin"
    TENANT_ADMIN = "tenant_admin"
    GOVERNANCE_ADMIN = "governance_admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


def require_roles(*allowed: RoleName) -> Callable:
    async def dependency() -> None:
        # Authentication/OIDC integration is intentionally deferred.
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Authorization is not configured; required roles: {', '.join(allowed)}",
        )

    return Depends(dependency)
