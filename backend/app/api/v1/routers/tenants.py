from fastapi import APIRouter, Depends

from app.core.tenancy import TenantContext, get_tenant_context

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("/context", summary="Return validated tenant request context")
async def read_tenant_context(
    context: TenantContext = Depends(get_tenant_context),
) -> dict[str, str]:
    return {"tenant_id": str(context.tenant_id)}
