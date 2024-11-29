from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from src.domain import repository
from src.schemas.auth import SessaoAutenticada
from src.utils import redirect_url_for


def authenticate(session: Session, request: Request, email: str, senha: str, lembrar_de_mim: bool = False) -> bool:
    db_usuario = repository.get(session, repository.Entities.USUARIO, {'email': email})
    if not db_usuario:
        return False

    senha_valida = str(senha).strip().lower() == str(db_usuario.senha).strip().lower()

    if not senha_valida:
        return False

    sessao = SessaoAutenticada(
        **db_usuario.dict(),
        valid=True
    )

    if not lembrar_de_mim:
        sessao.expires = (datetime.now()+timedelta(hours=1)).timestamp()

    request.session.update(sessao_autenticada=sessao.dict())
    return True


def usuario_autenticar(session: Session, request: Request, email: str, senha: str) -> bool:
    return authenticate(session, request, email, senha)


def request_login(session: Session, request: Request, email: str, senha: str, lembrar_de_mim: bool = False) -> RedirectResponse:
    try:
        authenticate(session, request, email, senha, lembrar_de_mim=lembrar_de_mim)
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

    if sessao_autenticada.expires and datetime.fromtimestamp(sessao_autenticada.expires) <= datetime.now():
        request.session.clear()
        raise HTTPException(401, 'Sessão expirada!')


HEADER_AUTH = Depends(header_authorization)
