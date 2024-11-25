import os

from fastapi import Depends, Request
from sqlmodel import SQLModel, create_engine

from src.auth import DBSessaoAutenticada

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


def reset():
    SQLModel.metadata.drop_all(bind=engine)
    SQLModel.metadata.create_all(bind=engine)
    return True


DBSESSAO_DEP = Depends(get_session)
