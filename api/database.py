from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") ## get URL from .env file
engine = create_async_engine(DATABASE_URL) ## take URL and create link to database
async_session = async_sessionmaker(engine, expire_on_commit=False) ## create session to database to keep objects in memory after commit

class Base(DeclarativeBase): ## turn python classes into database tables
    pass


async def get_db() -> AsyncSession: ## create function to get session to database
    async with async_session() as session:
        yield session