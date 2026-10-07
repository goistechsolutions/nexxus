from collections.abc import AsyncIterator
from uuid import UUID
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import get_settings
engine=create_async_engine(get_settings().database_url,pool_pre_ping=True,pool_size=10,max_overflow=20)
SessionLocal=async_sessionmaker(engine,expire_on_commit=False,autoflush=False)
@event.listens_for(engine.sync_engine,"checkout")
def scrub_connection(dbapi_connection,connection_record,connection_proxy):
    cursor=dbapi_connection.cursor()
    try:
        cursor.execute("RESET app.tenant_id")
        cursor.execute("RESET app.user_id")
    finally: cursor.close()
async def set_rls_context(session:AsyncSession,tenant_id:UUID,user_id:UUID)->None:
    # set_config(..., true) has SET LOCAL transaction scope and accepts bound parameters.
    await session.execute(text("SELECT set_config('app.tenant_id', :tenant_id, true)"),{"tenant_id":str(tenant_id)})
    await session.execute(text("SELECT set_config('app.user_id', :user_id, true)"),{"user_id":str(user_id)})
async def get_db()->AsyncIterator[AsyncSession]:
    async with SessionLocal() as session: yield session
async def tenant_session(tenant_id:UUID,user_id:UUID)->AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        async with session.begin():
            await set_rls_context(session,tenant_id,user_id)
            yield session
