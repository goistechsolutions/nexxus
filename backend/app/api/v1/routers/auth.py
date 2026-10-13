from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token, hash_jti
from app.models import RefreshToken
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    TokenPair,
)
from app.services.auth_service import authenticate, rotate, token_pair

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenPair)
async def login(
    body: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenPair:
    async with db.begin():
        user = await authenticate(db, body.tenant, body.email, body.password)
        if not user:
            raise HTTPException(status_code=401, detail="invalid credentials")
        return await token_pair(db, user)


@router.post("/refresh", response_model=TokenPair)
async def refresh(
    body: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenPair:
    try:
        async with db.begin():
            return await rotate(db, body.refresh_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail="invalid refresh token",
        ) from exc


@router.post("/logout", status_code=204)
async def logout(
    body: LogoutRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    try:
        claims = decode_token(body.refresh_token, "refresh")
    except ValueError:
        return

    async with db.begin():
        refresh_token = (
            await db.scalars(
                select(RefreshToken).where(
                    RefreshToken.jti_hash == hash_jti(str(claims["jti"]))
                )
            )
        ).first()
        if refresh_token:
            refresh_token.revoked_at = datetime.now(UTC)
