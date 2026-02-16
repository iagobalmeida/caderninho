from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends
from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from caderninho.src.env import getenv

database_url = getenv(
    key="DATABASE_URL",
    test_key="TEST_DATABASE_URL",
    default="sqlite+aiosqlite:///database.db",
)

engine = create_async_engine(
    database_url,
    # pool_size=10,
    # max_overflow=5,
    # pool_timeout=30,
    # pool_recycle=1800,
    echo=False,
)
async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def init_session():
    async with async_session_maker() as session:
        yield session


async def get_session():
    async with async_session_maker() as session:
        yield session


async def init():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def __drop_table(conn, table_name: str, cascade: bool = True):
    logger.info(f"Apagando tabela {table_name}")
    await conn.execute(
        text(f"DROP TABLE IF EXISTS {table_name} {'CASCADE' if cascade else ''};")
    )


async def __drop_tables(table_names: List[str], cascade: bool = True):
    async with engine.connect() as conn:
        for table_name in table_names:
            await __drop_table(conn, table_name, cascade)
        await conn.commit()


async def reset():
    await __drop_tables(
        table_names=[
            "receitagasto",
            "receita",
            "estoque",
            "venda",
            "insumo",
            "usuario",
        ],
        cascade="sqlite" not in database_url,
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    return True


DBSESSAO_DEP = Depends(get_session)
