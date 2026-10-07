from fastapi import APIRouter,Depends,Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
router=APIRouter(tags=["operations"])
@router.get("/live")
async def live():return {"status":"ok"}
@router.get("/ready")
async def ready(response:Response,db:AsyncSession=Depends(get_db)):
 try: await db.execute(text("SELECT 1")); return {"status":"ready"}
 except Exception: response.status_code=503; return {"status":"not-ready"}
