from typing import Annotated
from fastapi import APIRouter,Depends
from app.api.deps import principal
from app.core.context import AnalysisContext
router=APIRouter(prefix="/context",tags=["context"])
@router.get("")
async def current(ctx:Annotated[AnalysisContext,Depends(principal)]):return ctx
