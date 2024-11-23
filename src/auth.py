from datetime import datetime, timedelta
from typing import Dict
from uuid import uuid4

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
    id: int = None
    nome: str = None
    email: str = None
    dono: bool = None
    administrador: bool = False
    organizacao_id: int = None
    organizacao_descricao: str = None
    expires: datetime = None

    @property
    def expired(self):
        return self.expires <= datetime.now()

    def dict(self):
        base_dict = self.model_dump()
        del base_dict['expires']
        return base_dict

    def update(self, session: Session, nome: str, email: str):
        db_usuario = session.exec(select(Usuario).where(Usuario.id == self.id)).first()
        self.nome = nome
        db_usuario.nome = nome
        self.email = email
        db_usuario.email = email
        session.commit()
        return True


AUTHENTICATED_SESSIONS: Dict[str, SessionUser] = {}


def atualizar_sessao(session: Session, nome: str, email: str):
    sessao_usuario = session.info.get('auth_uuid', None)
    if not sessao_usuario or not AUTHENTICATED_SESSIONS.get(sessao_usuario, False):
        return False
    return AUTHENTICATED_SESSIONS[sessao_usuario].update(session, nome, email)


def criar_sessao(payload: SessionUser):
    global AUTHENTICATED_SESSIONS
    auth_uuid = str(uuid4())
    payload.update(expires=datetime.now() + timedelta(hours=1))
    payload.update(valid=True)
    AUTHENTICATED_SESSIONS[auth_uuid] = SessionUser(**payload)
    return auth_uuid


def usuario_de_sessao_db(session: Session) -> SessionUser:
    sessao_usuario_uuid = session.info.get('auth_uuid', None)
    sessao_usuario = AUTHENTICATED_SESSIONS.get(sessao_usuario_uuid, False)

    if not sessao_usuario_uuid or not sessao_usuario:
        raise HTTPException(401, 'É necessário se autenticar')

    if sessao_usuario.expired:
        del AUTHENTICATED_SESSIONS[sessao_usuario_uuid]
        raise HTTPException(401, 'Sua sessão expirou, autentique-se novamente')

    return sessao_usuario


def authenticate(session: Session, email: str, senha: str) -> str:
    db_usuario = session.exec(select(Usuario).where(Usuario.email == email)).first()
    if not db_usuario:
        return False

    senha_valida = str(senha).strip().lower() == str(db_usuario.senha).strip().lower()

    if not senha_valida:
        return False

    auth_uuid = criar_sessao(payload=db_usuario.dict())
    return jwt.encode(payload={'auth_uuid': auth_uuid}, key=DEFAULT_JWT_SECRET, algorithm=DEFAULT_JWT_ALG)


def header_authorization(request: Request, Authorization: str = Header(None)) -> str:
    jwt_payload = None

    if not Authorization:
        Authorization = request.cookies.get('jwt_token', None)

    try:
        jwt_payload = jwt.decode(Authorization, key=DEFAULT_JWT_SECRET, algorithms=[DEFAULT_JWT_ALG])
    except Exception as ex:
        pass

    if not jwt_payload or not jwt_payload.get('auth_uuid', False):
        raise HTTPException(401, 'Não autorizado!')

    query_params_theme = request.query_params.get('theme')
    if query_params_theme:
        request.state.theme = query_params_theme
        request.cookies.update(theme=query_params_theme)

    request.state.auth_uuid = jwt_payload.get('auth_uuid', None)


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
