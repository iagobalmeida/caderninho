from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from loguru import logger
from sqlmodel import Session

from src.domain import repository
from src.schemas.auth import AuthSession
from src.utils import redirect_url_for


async def authenticate(session: Session, request: Request, email: str, senha: str, lembrar_de_mim: bool = False) -> bool:
    auth_session = getattr(request.state, 'auth', None)
    db_usuario, _, _ = await repository.get(auth_session=auth_session, db_session=session, entity=repository.Entities.USUARIO, filters={'email': email}, first=True, ignore_validations=True)

    if not db_usuario:
        return False

    if db_usuario.organizacao and db_usuario.organizacao.plano_expiracao < datetime.now():
        await repository.update(
            auth_session=auth_session,
            db_session=session,
            entity=repository.Entities.ORGANIZACAO,
            filters={'id': db_usuario.organizacao_id},
            values={
                'plano_expiracao': datetime.now() + timedelta(days=7),
                'plano': repository.Plano.BLOQUEADO
            }
        )

    senha_valida = db_usuario.verificar_senha(senha)

    if not senha_valida:
        return False

    sessao = AuthSession(
        **db_usuario.model_dump(),
        organizacao_descricao=db_usuario.organizacao.descricao,
        valid=True
    )

    if not lembrar_de_mim:
        sessao.expires = (datetime.now()+timedelta(hours=1)).timestamp()

    request.session.update(sessao_autenticada=sessao.data_bs_payload())
    return True


async def usuario_autenticar(session: Session, request: Request, email: str, senha: str) -> bool:
    return await authenticate(session, request, email, senha)


async def request_login(session: Session, request: Request, email: str, senha: str, lembrar_de_mim: bool = False) -> RedirectResponse:
    try:
        await authenticate(session, request, email, senha, lembrar_de_mim=lembrar_de_mim)
        return redirect_url_for(request, 'get_home')
    except Exception as ex:  # pragma: nocover
        request.session.clear()
        logger.exception(ex)

        url = request.url_for('get_app_index')
        url = url.include_query_params(message=str(ex))

        return RedirectResponse(url, status_code=302)


async def request_logout(request: Request) -> RedirectResponse:
    response = redirect_url_for(request, 'get_app_index')
    request.session.clear()
    return response


def header_authorization(request: Request) -> str:
    request.state.auth = AuthSession.from_request_session(request)

    if not request.state.auth:
        request.session.clear()
        raise HTTPException(401, 'Não autorizado!')

    if request.state.auth.expires and datetime.fromtimestamp(request.state.auth.expires) <= datetime.now():
        request.session.clear()
        raise HTTPException(401, 'Sessão expirada!')

    if request.query_params.get('theme', None):
        request.session['theme'] = request.query_params.get('theme')
    elif not request.session.get('theme', None):
        request.session['theme'] = 'light'


HEADER_AUTH = Depends(header_authorization)
