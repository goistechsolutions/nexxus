from dataclasses import dataclass
from uuid import UUID

from fastapi import Header, HTTPException, status


@dataclass(frozen=True)
class TenantContext:
    tenant_id: UUID


async def get_tenant_context(
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
) -> TenantContext:
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-Id header is required",
        )
    try:
        return TenantContext(tenant_id=UUID(x_tenant_id))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-Id must be a UUID",
        ) from exc
