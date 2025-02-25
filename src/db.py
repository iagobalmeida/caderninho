from contextlib import contextmanager
from typing import List

from fastapi import Depends, Request
from loguru import logger
from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

from src.env import getenv

database_url = getenv('DATABASE_URL', "sqlite:///database.db")
engine = create_engine(database_url, echo=False)

DB_SESSION = None


@contextmanager
def init_session():
    global DB_SESSION
    DB_SESSION = Session(engine)
    logger.info('DB_SESSION started')
    try:
        yield
    except Exception as ex:
        pass
    finally:
        logger.info('DB_SESSION closed')
        DB_SESSION.close()


def get_session(request: Request):
    global DB_SESSION
    # __session = DB_SESSION
    # setattr(__session, 'sessao_autenticada', getattr(request.state, 'auth', None))  # TODO: Que poggzão!
    return DB_SESSION


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
