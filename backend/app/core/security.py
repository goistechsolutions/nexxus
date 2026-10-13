from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from typing import Annotated
from uuid import UUID, uuid4

import jwt
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext

from app.api.deps import principal
from app.core.config import get_settings
from app.core.context import AnalysisContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_context.verify(password, password_hash)


def hash_jti(jti: str) -> str:
    return sha256(jti.encode("utf-8")).hexdigest()


def _create_token(
    *,
    user_id: UUID,
    tenant_id: UUID,
    token_type: str,
    expires_delta: timedelta,
    permissions: list[str] | None = None,
) -> str:
    settings = get_settings()
    now = datetime.now(UTC)

    payload = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "token_type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "jti": uuid4().hex,
    }

    if permissions is not None:
        payload["permissions"] = permissions

    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def create_access_token(
    user_id: UUID,
    tenant_id: UUID,
    expires_in_minutes: int | None = None,
    permissions: list[str] | None = None,
) -> str:
    settings = get_settings()
    expires_in = expires_in_minutes or settings.access_token_expire_minutes

    return _create_token(
        user_id=user_id,
        tenant_id=tenant_id,
        token_type="access",
        expires_delta=timedelta(minutes=expires_in),
        permissions=permissions or [],
    )


def create_refresh_token(
    user_id: UUID,
    tenant_id: UUID,
    expires_in_days: int | None = None,
) -> str:
    settings = get_settings()
    expires_in = expires_in_days or settings.refresh_token_expire_days

    return _create_token(
        user_id=user_id,
        tenant_id=tenant_id,
        token_type="refresh",
        expires_delta=timedelta(days=expires_in),
    )


def decode_token(token: str, expected_type: str) -> dict[str, object]:
    settings = get_settings()

    try:
        claims = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError as exc:
        raise ValueError("invalid token") from exc

    if claims.get("token_type") != expected_type:
        raise ValueError("invalid token type")

    return claims


def require_permissions(*required: str) -> Callable:
    async def dependency(
        context: Annotated[AnalysisContext, Depends(principal)],
    ) -> AnalysisContext:
        if not set(required).issubset(context.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="missing permission",
            )
        return context

    return dependency
