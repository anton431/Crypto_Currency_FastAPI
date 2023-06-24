from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

import config

global_settings = config.get_settings()

engine = create_async_engine(
    global_settings.asyncpg_url,
    future=True,
    echo=True,
)

class Base(DeclarativeBase):
    pass


SessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False,
)

# Dependency
async def get_session() -> AsyncSession:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()



