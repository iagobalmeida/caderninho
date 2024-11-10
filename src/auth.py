import jwt
from fastapi import Depends, Header, Request
from sqlmodel import Session, select

from domain.entities import Usuario

DEFAULT_JWT_ALG = 'HS256'
DEFAULT_JWT_SECRET = b'secret'


def authenticate(session: Session, email: str, senha: str) -> str:
    db_usuario = session.exec(select(Usuario).where(Usuario.email == email)).first()
    if not db_usuario:
        return False
    senha_valida = str(senha).strip().lower() == str(db_usuario.senha).strip().lower()
    if not senha_valida:
        return False
    payload = db_usuario.model_dump()
    del payload['senha']
    return jwt.encode(payload=payload, key=DEFAULT_JWT_SECRET, algorithm=DEFAULT_JWT_ALG)


def header_authorization(request: Request, Authorization: str = Header(None)) -> str:
    user = None
    if not Authorization:
        Authorization = request.cookies.get('jwt_token')
    try:
        user = jwt.decode(Authorization, key=DEFAULT_JWT_SECRET, algorithms=[DEFAULT_JWT_ALG])
    except Exception as ex:
        print(ex)
    request.state.user = user


AUTH_DEP = Depends(header_authorization)
