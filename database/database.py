from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from constants import dotenv_path
from dotenv import load_dotenv
import os
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

HOST = os.getenv("ALCHEMY_DB_HOST")
NAME = os.getenv("ALCHEMY_DB_NAME")
USER = os.getenv("ALCHEMY_DB_USER")
PASSWORD = os.getenv("ALCHEMY_DB_PASSWORD")
PORT = os.getenv("ALCHEMY_DB_PORT")

database_url = f'postgresql+psycopg://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}'
database_async_url = f'postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}'

# sync
engine = create_engine(
    url=database_url,
    echo=False,
    max_overflow=10
)
session_factory = sessionmaker(engine, expire_on_commit=False, autoflush=False)
# async
async_engine = create_async_engine(
    url=database_async_url,
    echo=True,
    max_overflow=10
)
async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False, autoflush=False)


class Base(DeclarativeBase):
    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for index, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or index < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}\n")
        return f"<{self.__class__.__name__} {','.join(cols)}>"


async def get_aync_db():
    async with async_session_factory() as db:
        try:
            yield db
        finally:
            await db.close()


async def get_db():
    db = session_factory()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[AsyncSession, Depends(get_db)]
