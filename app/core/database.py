from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from typing import AsyncGenerator
from app.core.config import settings

#async database engine
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://","postgresql+asyncpg://"),
    echo = settings.DEBUG,
    future = True,
    pool_pre_ping = True,
)

#sessino facrtor (har request ke liye naya session)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit = False,
    autocommit = False,
    autoflush = False
)

#base class for all models
Base = declarative_base()

async def get_db() ->AsyncGenerator[AsyncSession, None]:
    """
    Databasse Session dependency.
    it is used to get a database session for each request.
    @app.get("/users")
    async def get_users(db: AsyncSession = Depends(get_db)):
        # db use 
        pass
    """

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit() #changes saved
        
        except Exception:
            await session.rollback()
            raise

        finally:
            await session.close()


async def init_db():
    """Database initialization ie table creation"""

    async with engine.begin() as conn:

        #table creation
        await conn.run_sync(Base.metadata.create_all)
        print("Database initialized with tables")


async def close_db():
    """Database closing"""
    await engine.dispose()
    print("Database connection closed")