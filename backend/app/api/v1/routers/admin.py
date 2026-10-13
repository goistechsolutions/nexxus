from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import principal, require_permissions, tenant_db
from app.core.context import AnalysisContext
from app.core.security import hash_password
from app.models import Permission, Role, User
from app.schemas.admin import RoleCreate, UserCreate

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post(
    "/roles",
    dependencies=[Depends(require_permissions("roles:write"))],
)
async def create_role(
    body: RoleCreate,
    context: Annotated[AnalysisContext, Depends(principal)],
    db: AsyncSession = Depends(tenant_db),
) -> dict[str, str]:
    permissions = (
        await db.scalars(
            select(Permission).where(Permission.code.in_(body.permissions))
        )
    ).all()

    if len(permissions) != len(set(body.permissions)):
        raise HTTPException(status_code=400, detail="unknown permission")

    role = Role(
        tenant_id=context.tenant_id,
        name=body.name,
        permissions=list(permissions),
    )
    db.add(role)
    await db.flush()

    return {"id": str(role.id), "name": role.name}


@router.post(
    "/users",
    dependencies=[Depends(require_permissions("users:write"))],
)
async def create_user(
    body: UserCreate,
    context: Annotated[AnalysisContext, Depends(principal)],
    db: AsyncSession = Depends(tenant_db),
) -> dict[str, str]:
    roles = (
        await db.scalars(select(Role).where(Role.name.in_(body.roles)))
    ).all()

    user = User(
        tenant_id=context.tenant_id,
        email=body.email.lower(),
        password_hash=hash_password(body.password),
        roles=list(roles),
    )
    db.add(user)
    await db.flush()

    return {"id": str(user.id), "email": user.email}
