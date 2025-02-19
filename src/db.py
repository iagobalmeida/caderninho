import os
from typing import List

from fastapi import Depends, Request
from sqlalchemy import text
from sqlmodel import SQLModel, create_engine

from src.schemas.auth import DBSessaoAutenticada

sqlite_nome_arquivo = "database.db"
sqlite_url = f"sqlite:///{sqlite_nome_arquivo}"

DATABASE_URL = os.getenv('DATABASE_URL', sqlite_url)

engine = create_engine(DATABASE_URL, echo=False)


def get_session(request: Request):
    with DBSessaoAutenticada(engine, request=request) as session:
        yield session
    session.close()


def init():
    SQLModel.metadata.create_all(engine)


def __drop_table(conn, table_name: str, cascade: bool = True):
    conn.execute(text(f"DROP TABLE IF EXISTS {table_name} {'CASCADE' if cascade else ''};"))


def __drop_tables(table_names: List[str], cascade: bool = True):
    with engine.connect() as conn:
        for table_name in table_names:
            __drop_table(conn, table_name, cascade)
        conn.commit()


def reset():
    __drop_tables(
        table_names=[
            'receitainsumolink',
            'receita',
            'estoque',
            'venda',
            'insumo',
            'usuario'
        ],
        cascade='sqlite' not in DATABASE_URL
    )
    SQLModel.metadata.drop_all(bind=engine)
    SQLModel.metadata.create_all(bind=engine)
    return True


DBSESSAO_DEP = Depends(get_session)
