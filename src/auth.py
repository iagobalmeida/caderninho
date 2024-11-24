from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlmodel import Session, select

from src.domain.entities import Usuario
from src.utils import redirect_url_for


class SessaoAutenticada(BaseModel):
    valid: bool = False
    id: int = None
    nome: str = None
    email: str = None
    dono: bool = None
    administrador: bool = False
    organizacao_id: int = None
    organizacao_descricao: str = None
    expires: float = None

    @classmethod
    def from_request_session(cls, request: Request):
        request_session_sessao_autenticada = request.session.get('sessao_autenticada', None)
        if request_session_sessao_autenticada:
            return cls(**request_session_sessao_autenticada)

    def dict(self):
        return self.model_dump()


class DBSessaoAutenticada(Session):
    sessao_autenticada: SessaoAutenticada = None

    def __init__(self, *args, request: Request = None, **kwargs):
        self.sessao_autenticada = SessaoAutenticada.from_request_session(request)
        return super().__init__(*args, **kwargs)


def authenticate(session: Session, request: Request, email: str, senha: str) -> bool:
    db_usuario = session.exec(select(Usuario).where(Usuario.email == email)).first()
    if not db_usuario:
        return False

    senha_valida = str(senha).strip().lower() == str(db_usuario.senha).strip().lower()

    if not senha_valida:
        return False

    sessao = SessaoAutenticada(
        **db_usuario.dict(),
        expires=(datetime.now()+timedelta(hours=1)).timestamp(),
        valid=True
    )

    request.session.update(sessao_autenticada=sessao.dict())
    return True


def usuario_autenticar(session: Session, request: Request, email: str, senha: str) -> bool:
    return authenticate(session, request, email, senha)


def request_login(session: Session, request: Request, email: str, senha: str) -> RedirectResponse:
    try:
        authenticate(session, request, email, senha)
        return redirect_url_for(request, 'get_home')
    except Exception as ex:
        request.session.clear()

        url = request.url_for('get_index')
        url = url.include_query_params(message=str(ex))

        return RedirectResponse(url, status_code=302)


def request_logout(request: Request) -> RedirectResponse:
    response = redirect_url_for(request, 'get_index')
    request.session.clear()
    return response


def header_authorization(request: Request) -> str:
    sessao_autenticada = SessaoAutenticada.from_request_session(request)
    if not sessao_autenticada:
        request.session.clear()
        raise HTTPException(401, 'Não autorizado!')

    if datetime.fromtimestamp(sessao_autenticada.expires) <= datetime.now():
        request.session.clear()
        raise HTTPException(401, 'Sessão expirada!')


HEADER_AUTH = Depends(header_authorization)
