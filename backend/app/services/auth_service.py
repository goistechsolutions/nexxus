from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_jti,
    verify_password,
)
from app.models import RefreshToken, Role, Tenant, User


async def permissions(user: User) -> list[str]:
    return sorted(
        {permission.code for role in user.roles for permission in role.permissions}
    )


async def authenticate(
    db: AsyncSession,
    tenant_slug: str,
    email: str,
    password: str,
) -> User | None:
    query = (
        select(User)
        .join(Tenant)
        .options(
            selectinload(User.roles).selectinload(Role.permissions)
        )
        .where(
            Tenant.slug == tenant_slug,
            Tenant.active.is_(True),
            User.email == email.lower(),
            User.active.is_(True),
        )
    )

    user = (await db.scalars(query)).first()

    if not user or not verify_password(password, user.password_hash):
        return None

    return user


async def token_pair(db: AsyncSession, user: User) -> dict[str, object]:
    user_permissions = await permissions(user)

    access_token = create_access_token(
        user_id=user.id,
        tenant_id=user.tenant_id,
        token_version=user.token_version,
        permissions=user_permissions,
    )

    refresh_token, jti, expires_at = create_refresh_token(
        user_id=user.id,
        tenant_id=user.tenant_id,
        token_version=user.token_version,
    )

    db.add(
        RefreshToken(
            user_id=user.id,
            tenant_id=user.tenant_id,
            jti_hash=hash_jti(jti),
            expires_at=expires_at,
        )
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 900,
    }


async def rotate(db: AsyncSession, raw_refresh_token: str) -> dict[str, object]:
    claims = decode_token(raw_refresh_token, "refresh")

    stored_token = (
        await db.scalars(
            select(RefreshToken).where(
                RefreshToken.jti_hash == hash_jti(str(claims["jti"])),
                RefreshToken.revoked_at.is_(None),
            )
        )
    ).first()

    if not stored_token or stored_token.expires_at <= datetime.now(UTC):
        raise ValueError("invalid refresh token")

    user = (
        await db.scalars(
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .where(
                User.id == UUID(str(claims["sub"])),
                User.active.is_(True),
            )
        )
    ).first()

    if not user or user.token_version != int(claims["ver"]):
        raise ValueError("invalid refresh token")

    stored_token.revoked_at = datetime.now(UTC)

    return await token_pair(db, user)
