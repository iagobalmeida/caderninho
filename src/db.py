from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

sqlite_nome_arquivo = "database.db"
sqlite_url = f"sqlite:///{sqlite_nome_arquivo}"

engine = create_engine(sqlite_url, echo=True)


def get_session():
    with Session(engine) as session:
        yield session
    session.close()


def init():
    SQLModel.metadata.create_all(engine)


SESSION_DEP = Depends(get_session)
