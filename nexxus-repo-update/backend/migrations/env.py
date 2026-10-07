import asyncio
from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from app.core.config import get_settings
from app.models import Base
config=context.config; config.set_main_option("sqlalchemy.url",get_settings().database_url); target_metadata=Base.metadata
def offline():
 context.configure(url=config.get_main_option("sqlalchemy.url"),target_metadata=target_metadata,literal_binds=True,compare_type=True)
 with context.begin_transaction():context.run_migrations()
def sync_run(conn):
 context.configure(connection=conn,target_metadata=target_metadata,compare_type=True)
 with context.begin_transaction():context.run_migrations()
async def online_async():
 engine=async_engine_from_config(config.get_section(config.config_ini_section),prefix="sqlalchemy.",poolclass=pool.NullPool)
 async with engine.connect() as conn:await conn.run_sync(sync_run)
 await engine.dispose()
def online():asyncio.run(online_async())
offline() if context.is_offline_mode() else online()
