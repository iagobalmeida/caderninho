from contextlib import contextmanager
from typing import List

from fastapi import Depends
from loguru import logger
from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

from src.env import getenv

database_url = getenv('DATABASE_URL', "sqlite:///database.db")
engine = create_engine(
    database_url,
    pool_size=10,
    max_overflow=5,
    pool_timeout=30,
    pool_recycle=1800,
    echo=False
)
SessionLocal = Session(engine)


@contextmanager
def init_session():
    session = SessionLocal
    try:
        if (engine.echo):
            logger.info(engine.pool.status())
        yield session
    finally:
        session.close()


def get_session():
    with init_session() as session:
        yield session


def init():
    SQLModel.metadata.create_all(engine)


def __drop_table(conn, table_name: str, cascade: bool = True):
    logger.info(f'Apagando tabela {table_name}')
    conn.execute(text(f"DROP TABLE IF EXISTS {table_name} {'CASCADE' if cascade else ''};"))


def __drop_tables(table_names: List[str], cascade: bool = True):
    with engine.connect() as conn:
        for table_name in table_names:
            __drop_table(conn, table_name, cascade)
        conn.commit()


def reset():
    database_url = getenv('DATABASE_URL', "sqlite:///database.db")
    __drop_tables(
        table_names=[
            'receitainsumolink',
            'receita',
            'estoque',
            'venda',
            'insumo',
            'usuario'
        ],
        cascade='sqlite' not in database_url
    )
    SQLModel.metadata.drop_all(bind=engine)
    SQLModel.metadata.create_all(bind=engine)
    return True


DBSESSAO_DEP = Depends(get_session)
