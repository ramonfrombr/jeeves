import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_async_engine(os.environ.get("DATABASE_URL"), echo=True)
AsyncSessionLocal = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
