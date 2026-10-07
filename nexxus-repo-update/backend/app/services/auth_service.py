from datetime import datetime,timezone
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.security import create_access_token,create_refresh_token,decode_token,hash_jti,verify_password
from app.models import RefreshToken,Tenant,User
async def permissions(user:User)->list[str]:return sorted({p.code for r in user.roles for p in r.permissions})
async def authenticate(db:AsyncSession,tenant_slug:str,email:str,password:str)->User|None:
 q=select(User).join(Tenant).options(selectinload(User.roles).selectinload(__import__('app.models',fromlist=['Role']).Role.permissions)).where(Tenant.slug==tenant_slug,Tenant.active.is_(True),User.email==email.lower(),User.active.is_(True))
 user=(await db.scalars(q)).first();return user if user and verify_password(password,user.password_hash) else None
async def token_pair(db:AsyncSession,user:User)->dict:
 perms=await permissions(user);access=create_access_token(user.id,user.tenant_id,user.token_version,perms);refresh,jti,expires=create_refresh_token(user.id,user.tenant_id,user.token_version);db.add(RefreshToken(user_id=user.id,tenant_id=user.tenant_id,jti_hash=hash_jti(jti),expires_at=expires));return {"access_token":access,"refresh_token":refresh,"token_type":"bearer","expires_in":900}
async def rotate(db:AsyncSession,raw:str)->dict:
 c=decode_token(raw,"refresh");row=(await db.scalars(select(RefreshToken).where(RefreshToken.jti_hash==hash_jti(c["jti"]),RefreshToken.revoked_at.is_(None)))).first()
 if not row or row.expires_at<=datetime.now(timezone.utc):raise ValueError("invalid refresh token")
 user=(await db.scalars(select(User).options(selectinload(User.roles).selectinload(__import__('app.models',fromlist=['Role']).Role.permissions)).where(User.id==UUID(c["sub"]),User.active.is_(True)))).first()
 if not user or user.token_version!=c["ver"]:raise ValueError("invalid refresh token")
 row.revoked_at=datetime.now(timezone.utc);return await token_pair(db,user)
