from collections.abc import AsyncIterator
from typing import Annotated, Callable
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select

from app.core.context import AnalysisContext
from app.core.database import SessionLocal, set_rls_context
from app.core.security import decode_token
from app.models import User

bearer = HTTPBearer()


async def principal(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
    x_tenant_id: Annotated[UUID | None, Header()] = None,
) -> AnalysisContext:
    try:
        claims = decode_token(credentials.credentials, "access")
        tenant_id = UUID(claims["tenant_id"])
        user_id = UUID(claims["sub"])
    except Exception as exc:
        raise HTTPException(status_code=401, detail="invalid token") from exc

    if x_tenant_id and x_tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="tenant mismatch")

    return AnalysisContext(
        user_id=user_id,
        tenant_id=tenant_id,
        roles=frozenset(claims.get("permissions", [])),
        correlation_id=request.state.correlation_id,
    )


async def tenant_db(
    context: Annotated[AnalysisContext, Depends(principal)],
) -> AsyncIterator:
    async with SessionLocal() as db:
        async with db.begin():
            await set_rls_context(db, context.tenant_id, context.user_id)

            user = (
                await db.scalars(
                    select(User).where(
                        User.id == context.user_id,
                        User.active.is_(True),
                    )
                )
            ).first()

            if not user:
                raise HTTPException(status_code=401, detail="inactive user")

            yield db


def require_permissions(*required: str) -> Callable:
    async def dependency(
        context: Annotated[AnalysisContext, Depends(principal)],
    ) -> AnalysisContext:
        if not set(required).issubset(context.roles):
            raise HTTPException(status_code=403, detail="missing permission")
        return context

    return dependency
