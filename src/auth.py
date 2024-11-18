import jwt
from fastapi import Depends, Header, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlmodel import Session, select

from src.domain.entities import Usuario
from src.utils import redirect_url_for

DEFAULT_JWT_ALG = 'HS256'
DEFAULT_JWT_SECRET = b'secret'


class SessionUser(BaseModel):
    valid: bool = False
    nome: str = None
    email: str = None
    administrador: bool = False
    organizacao_id: int = None
    organizacao_nome: str = None


def usuario_de_sessao(session: Session) -> SessionUser:
    sessao_usuario = session.info.get('user', None)
    if not sessao_usuario:
        return SessionUser(valid=False)
    return SessionUser(**sessao_usuario, valid=True)


def authenticate(session: Session, email: str, senha: str) -> str:
    db_usuario = session.exec(select(Usuario).where(Usuario.email == email)).first()

    if not db_usuario:
        return False
    senha_valida = str(senha).strip().lower() == str(db_usuario.senha).strip().lower()

    if not senha_valida:
        return False

    payload = db_usuario.dict()
    return jwt.encode(payload=payload, key=DEFAULT_JWT_SECRET, algorithm=DEFAULT_JWT_ALG)


def header_authorization(request: Request, Authorization: str = Header(None)) -> str:
    user = None

    if not Authorization:
        Authorization = request.cookies.get('jwt_token', None)

    try:
        user = jwt.decode(Authorization, key=DEFAULT_JWT_SECRET, algorithms=[DEFAULT_JWT_ALG])
    except Exception as ex:
        pass

    if not user:
        raise HTTPException(401, 'Não autorizado!')

    query_params_theme = request.query_params.get('theme')
    if query_params_theme:
        request.state.theme = query_params_theme
        request.cookies.update(theme=query_params_theme)

    request.state.user = user
    return user


def request_login(session: Session, request: Request, email: str, senha: str) -> RedirectResponse:
    jwt_token = authenticate(session, email=email, senha=senha)
    if jwt_token:
        response = redirect_url_for(request, 'get_home')
        response.set_cookie('jwt_token', jwt_token)
    else:
        url = request.url_for('get_index')
        url = url.include_query_params(message='Email e/ou senha inválidos!')
        response = RedirectResponse(url, status_code=302)
        response.delete_cookie('jwt_token')
    return response


def request_logout(request: Request) -> RedirectResponse:
    response = redirect_url_for(request, 'get_index')
    response.delete_cookie('jwt_token')
    return response


HEADER_AUTH = Depends(header_authorization)
