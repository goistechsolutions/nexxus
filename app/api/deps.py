from collections.abc import AsyncIterator
from typing import Annotated,Callable
from uuid import UUID
from fastapi import Depends,Header,HTTPException,Request
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.context import AnalysisContext
from app.core.database import SessionLocal,set_rls_context
from app.core.security import decode_token
from app.models import User
bearer=HTTPBearer()
async def principal(request:Request,credentials:Annotated[HTTPAuthorizationCredentials,Depends(bearer)],x_tenant_id:Annotated[str|None,Header()]=None)->AnalysisContext:
 try:c=decode_token(credentials.credentials,"access");tid=UUID(c["tenant_id"]);uid=UUID(c["sub"])
 except Exception as exc:raise HTTPException(401,"invalid token") from exc
 if x_tenant_id and UUID(x_tenant_id)!=tid:raise HTTPException(403,"tenant mismatch")
 return AnalysisContext(uid,tid,frozenset(c.get("permissions",[])),request.state.correlation_id)
async def tenant_db(ctx:Annotated[AnalysisContext,Depends(principal)])->AsyncIterator:
 async with SessionLocal() as db:
  async with db.begin():
   await set_rls_context(db,ctx.tenant_id,ctx.user_id)
   user=(await db.scalars(select(User).where(User.id==ctx.user_id,User.active.is_(True)))).first()
   if not user:raise HTTPException(401,"inactive user")
   yield db
def require_permissions(*required:str)->Callable:
 async def dep(ctx:Annotated[AnalysisContext,Depends(principal)]):
  if not set(required).issubset(ctx.roles):raise HTTPException(403,"missing permission")
  return ctx
 return dep
