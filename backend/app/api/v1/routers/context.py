from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import principal
from app.core.context import AnalysisContext

router = APIRouter(tags=["context"])


@router.get("/context", summary="Return the authenticated request context")
async def read_context(
    context: Annotated[AnalysisContext, Depends(principal)],
) -> dict[str, str]:
    return {
        "user_id": str(context.user_id),
        "tenant_id": str(context.tenant_id),
        "correlation_id": context.correlation_id,
    }
