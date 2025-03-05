import logging
import random
import re
from datetime import datetime, timedelta

import fastapi
import fastapi.security
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.log import rootlogger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from src import db
from src.domain import inputs, repository
from src.modules import smpt
from src.modules.logger import logger, setup_logger
from src.routers.autenticacao import router as router_autenticacao
from src.routers.caixa_movimentacoes import \
    router as router_caixa_movimentacoes
from src.routers.estoques import router as router_estoques
from src.routers.insumos import router as router_insumos
from src.routers.organizacao import router as router_organizacao
from src.routers.paginas import router as router_paginas
from src.routers.receitas import router as router_receitas
from src.routers.scripts import router as router_scripts
from src.templates import render
from src.utils import url_incluir_query_params

setup_logger()

SESSION_SECRET_KEY = 'SESSION_SECRET_KEY'

rootlogger.setLevel(logging.WARN)


app = fastapi.FastAPI(on_startup=[db.init])
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY, https_only=False)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
    expose_headers=[
        'X-Content-Type-Options', 'X-Frame-Options', 'X-XSS-Protection', 'Content-Security-Policy', 'Strict-Transport-Security'
    ]
)

app.include_router(router_receitas)
app.include_router(router_insumos)
app.include_router(router_estoques)
app.include_router(router_caixa_movimentacoes)
app.include_router(router_organizacao)
app.include_router(router_scripts)
app.include_router(router_autenticacao)
app.include_router(router_paginas)
app.mount("/static", StaticFiles(directory="src/static"), name="static")


class CacheControlMiddleware(BaseHTTPMiddleware):  # pragma:nocover
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/static/"):
            response.headers["Cache-Control"] = "public, max-age=3600"
        return response


app.add_middleware(CacheControlMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=500)


@app.get("/android-chrome-192x192.png")
async def android_chrome_192x192_png(request: fastapi.Request):
    return RedirectResponse('/static/favicon/android-chrome-192x192.png')


@app.get('/', include_in_schema=False)
async def get_index(request: fastapi.Request):
    return await render(request, 'index.html', context={
        'body_class': 'index'
    })


@app.get('/app', include_in_schema=False)
async def get_app_index(request: fastapi.Request, message: str = fastapi.Query(None),  error: str = fastapi.Query(None)):
    return await render(request, 'autenticacao/login.html', context={'message': message, 'error': error, 'data_bs_theme': 'auto'})


@app.get('/app/registrar', include_in_schema=False)
async def get_registrar(request: fastapi.Request, message: str = fastapi.Query(None),  error: str = fastapi.Query(None)):
    return await render(request, 'autenticacao/criar_conta.html', context={'message': message, 'error': error, 'data_bs_theme': 'auto'})


@app.post('/app/registrar', include_in_schema=False)
async def post_registrar(request: fastapi.Request, payload: inputs.UsuarioCriar = fastapi.Form(), error: str = fastapi.Query(None), session: db.Session = db.DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    template_name = 'autenticacao/login.html'
    message = None
    try:
        if payload.senha != payload.senha_confirmar:
            raise ValueError('As senhas não batem')

        db_organizacao = await repository.create(auth_session=auth_session, db_session=session, entity=repository.Entities.ORGANIZACAO, values={
            'descricao': payload.organizacao_descricao,
            'plano': payload.plano,
            'plano_expiracao': datetime.now() + timedelta(days=1)
        })
        organizacao_id = db_organizacao.id

        await repository.create(auth_session=auth_session, db_session=session, entity=repository.Entities.USUARIO, values={
            'nome': payload.nome,
            'email': payload.email,
            'senha': payload.senha,
            'organizacao_id': organizacao_id,
            'dono': True
        })
        message = 'Conta criada com sucesso'
    except Exception as ex:
        logger.exception(ex)
        template_name = 'autenticacao/criar_conta.html'
        error = str(ex)

    return await render(request, template_name, context={'error': error, 'message': message, 'data_bs_theme': 'auto'})


@app.get('/app/recuperar_senha', include_in_schema=False)
async def get_recuperar_senha(request: fastapi.Request, message: str = fastapi.Query(None),  error: str = fastapi.Query(None)):
    return await render(request, 'autenticacao/recuperar_senha.html', context={'message': message, 'error': error, 'data_bs_theme': 'auto'})


@app.post('/app/recuperar_senha', include_in_schema=False)
async def post_recuperar_senha(request: fastapi.Request, email: str = fastapi.Form(), message: str = fastapi.Query(None),  error: str = fastapi.Query(None), session: db.AsyncSession = db.DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    db_usuario, _, _ = await repository.get(auth_session=auth_session, db_session=session, entity=repository.Entities.USUARIO, filters={'email': email}, first=True)
    if not db_usuario:
        raise ValueError('Não foi encontrado usuário com esse email')

    nova_senha = str(random.randint(int('1'*9), int('9'*9)))
    db_usuario.senha = nova_senha
    db_usuario.hash_senha()
    await session.commit()

    smpt.enviar(
        assunto='KDerninho - Recuperar Senha',
        corpo=f'Sua nova senha temporária é {nova_senha}',
        para=[db_usuario.email]
    )
    return await render(request, 'autenticacao/login.html', context={'message': f'Senha enviada para: {db_usuario.email}', 'error': error, 'data_bs_theme': 'auto'})


@app.exception_handler(IntegrityError)  # pragma: nocover
async def integrity_error_exception_handler(request: fastapi.Request, ex, redirect_to: str = None):
    logger.exception(ex)
    if not redirect_to:
        base_redirect = request.url_for('get_app_index')
        if request.session.get('sessao_autenticada', False):
            base_redirect = request.url_for('get_home')
        redirect_to = str(request.headers.get('referer', base_redirect))

        redirect_to = str(request.headers.get('referer', base_redirect))

    error = f'<span>Verifique os campos preenchidos'
    detalhe = re.search(r'\.(\w+)$', str(ex.orig))
    if detalhe:
        detalhe = detalhe.group(1)
        error = f'<span>Campo&nbsp;<code>{detalhe}</code>&nbsp;inválido'

    redirect_to = url_incluir_query_params(redirect_to, error=error)
    return fastapi.responses.RedirectResponse(redirect_to, status_code=302)


@app.exception_handler(ValueError)  # pragma: nocover
async def value_error_exception_handler(request: fastapi.Request, ex, redirect_to: str = None):
    if not isinstance(ex, HTTPException):
        logger.exception(ex)
    if not redirect_to:
        base_redirect = request.url_for('get_app_index')
        if request.session.get('sessao_autenticada', False):
            base_redirect = request.url_for('get_home')
        redirect_to = str(request.headers.get('referer', base_redirect))

    redirect_to = url_incluir_query_params(redirect_to, error=str(ex))
    return fastapi.responses.RedirectResponse(redirect_to, status_code=302)


@app.exception_handler(HTTPException)  # pragma: nocover
async def http_error_exception_handler(request: fastapi.Request, ex: HTTPException):
    if ex.status_code == 401:
        request.session.clear()
        redirect_to = request.url_for('get_app_index')
        logger.warning('Não autorizado')
    else:
        logger.exception(ex)

        base_redirect = request.url_for('get_app_index')
        if request.session.get('sessao_autenticada', False):
            base_redirect = request.url_for('get_home')

        redirect_to = str(request.headers.get('referer', base_redirect))
    return await value_error_exception_handler(request, ex, redirect_to=redirect_to)


@app.exception_handler(RequestValidationError)  # pragma: nocover
async def generic_exception_handler(request: fastapi.Request, ex: Exception):
    logger.exception(ex)

    base_redirect = request.url_for('get_app_index')
    if request.session.get('sessao_autenticada', False):
        base_redirect = request.url_for('get_home')

    redirect_to = str(request.headers.get('referer', base_redirect))
    redirect_to = url_incluir_query_params(redirect_to, error=ex.errors()[0]["msg"])
    return fastapi.responses.RedirectResponse(redirect_to, status_code=302)
