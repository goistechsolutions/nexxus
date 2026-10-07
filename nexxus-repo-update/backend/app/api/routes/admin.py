from typing import Annotated
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import principal,require_permissions,tenant_db
from app.core.context import AnalysisContext
from app.core.security import hash_password
from app.models import Permission,Role,User
from app.schemas.admin import RoleCreate,UserCreate
router=APIRouter(prefix="/admin",tags=["admin"])
@router.post("/roles",dependencies=[Depends(require_permissions("roles:write"))])
async def create_role(body:RoleCreate,ctx:Annotated[AnalysisContext,Depends(principal)],db:AsyncSession=Depends(tenant_db)):
 perms=(await db.scalars(select(Permission).where(Permission.code.in_(body.permissions)))).all()
 if len(perms)!=len(set(body.permissions)):raise HTTPException(400,"unknown permission")
 role=Role(tenant_id=ctx.tenant_id,name=body.name,permissions=list(perms));db.add(role);await db.flush();return {"id":role.id,"name":role.name}
@router.post("/users",dependencies=[Depends(require_permissions("users:write"))])
async def create_user(body:UserCreate,ctx:Annotated[AnalysisContext,Depends(principal)],db:AsyncSession=Depends(tenant_db)):
 roles=(await db.scalars(select(Role).where(Role.name.in_(body.roles)))).all();user=User(tenant_id=ctx.tenant_id,email=body.email.lower(),password_hash=hash_password(body.password),roles=list(roles));db.add(user);await db.flush();return {"id":user.id,"email":user.email}
