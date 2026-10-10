from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.auth import LoginRequest,RefreshRequest,LogoutRequest,TokenPair
from app.services.auth_service import authenticate,rotate,token_pair
from app.core.security import decode_token,hash_jti
from app.models import RefreshToken
from sqlalchemy import select
from datetime import datetime,timezone
router=APIRouter(prefix="/auth",tags=["auth"])
@router.post("/login",response_model=TokenPair)
async def login(body:LoginRequest,db:AsyncSession=Depends(get_db)):
 async with db.begin():
  user=await authenticate(db,body.tenant,body.email,body.password)
  if not user:raise HTTPException(401,"invalid credentials")
  return await token_pair(db,user)
@router.post("/refresh",response_model=TokenPair)
async def refresh(body:RefreshRequest,db:AsyncSession=Depends(get_db)):
 try:
  async with db.begin():return await rotate(db,body.refresh_token)
 except Exception as exc:raise HTTPException(401,"invalid refresh token") from exc
@router.post("/logout",status_code=204)
async def logout(body:LogoutRequest,db:AsyncSession=Depends(get_db)):
 try:c=decode_token(body.refresh_token,"refresh")
 except Exception: return
 async with db.begin():
  row=(await db.scalars(select(RefreshToken).where(RefreshToken.jti_hash==hash_jti(c["jti"])))).first()
  if row:row.revoked_at=datetime.now(timezone.utc)
