from fastapi import Depends, Request
from sqlmodel import Session, SQLModel, create_engine

sqlite_nome_arquivo = "database.db"
sqlite_url = f"sqlite:///{sqlite_nome_arquivo}"

engine = create_engine(sqlite_url, echo=False)


def get_session(request: Request):
    with Session(engine) as session:
        session.info.update(user=request.state.user)
        yield session
    session.close()


def init():
    SQLModel.metadata.create_all(engine)


SESSION_DEP = Depends(get_session)
