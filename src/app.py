
import logging
import random
import re

import fastapi
import fastapi.security
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from sqlalchemy.log import rootlogger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from src import db
from src.domain import inputs, repository
from src.modules import send_email
from src.modules.logger import logger, setup_logger
from src.routers.autenticacao import router as router_autenticacao
from src.routers.estoques import router as router_estoques
from src.routers.insumos import router as router_insumos
from src.routers.organizacao import router as router_organizacao
from src.routers.paginas import router as router_paginas
from src.routers.receitas import router as router_receitas
from src.routers.scripts import router as router_scripts
from src.routers.vendas import router as router_vendas
from src.schemas.auth import DBSessaoAutenticada
from src.templates import render
from src.utils import url_incluir_query_params

setup_logger()

SESSION_SECRET_KEY = 'SESSION_SECRET_KEY'

rootlogger.setLevel(logging.WARN)

app = fastapi.FastAPI()
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY, https_only=False)

app.include_router(router_receitas)
app.include_router(router_insumos)
app.include_router(router_estoques)
app.include_router(router_vendas)
app.include_router(router_organizacao)
app.include_router(router_scripts)
app.include_router(router_autenticacao)
app.include_router(router_paginas)
app.mount("/static", StaticFiles(directory="src/static"), name="static")


class CacheControlMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/static/"):
            response.headers["Cache-Control"] = "public, max-age=3600"
        return response


app.add_middleware(CacheControlMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=500)

db.init()


@app.get('/', include_in_schema=False)
async def get_index(request: fastapi.Request):
    return render(request, 'index.html', context={
        'body_class': 'index'
    })


@app.get('/app', include_in_schema=False)
async def get_app_index(request: fastapi.Request, message: str = fastapi.Query(None),  error: str = fastapi.Query(None)):
    return render(request, 'autenticacao/login.html', context={'message': message, 'error': error, 'data_bs_theme': 'auto'})


@app.get('/app/registrar', include_in_schema=False)
async def get_registrar(request: fastapi.Request, message: str = fastapi.Query(None),  error: str = fastapi.Query(None)):
    return render(request, 'autenticacao/criar_conta.html', context={'message': message, 'error': error, 'data_bs_theme': 'auto'})


@app.post('/app/registrar', include_in_schema=False)
async def post_registrar(request: fastapi.Request, payload: inputs.UsuarioCriar = fastapi.Form(), error: str = fastapi.Query(None), session: DBSessaoAutenticada = db.DBSESSAO_DEP):
    template_name = 'autenticacao/login.html'
    message = None
    try:
        if payload.senha != payload.senha_confirmar:
            raise Exception('As senhas não batem')

        db_organizacao = repository.create(session, repository.Entities.ORGANIZACAO, {'descricao': payload.organizacao_descricao})
        organizacao_id = db_organizacao.id

        repository.create(session, repository.Entities.USUARIO, {
            'nome': payload.nome,
            'email': payload.email,
            'senha': payload.senha,
            'organizacao_id': organizacao_id,
            'dono': True
        })
        message = 'Conta criada com sucesso'
    except Exception as ex:
        template_name = 'autenticacao/criar_conta.html'
        error = str(ex)

    return render(request, template_name, context={'error': error, 'message': message, 'data_bs_theme': 'auto'})


@app.get('/app/recuperar_senha', include_in_schema=False)
async def get_recuperar_senha(request: fastapi.Request, message: str = fastapi.Query(None),  error: str = fastapi.Query(None)):
    return render(request, 'autenticacao/recuperar_senha.html', context={'message': message, 'error': error, 'data_bs_theme': 'auto'})


@app.post('/app/recuperar_senha', include_in_schema=False)
async def post_recuperar_senha(request: fastapi.Request, email: str = fastapi.Form(), message: str = fastapi.Query(None),  error: str = fastapi.Query(None), session: DBSessaoAutenticada = db.DBSESSAO_DEP):
    db_usuario, _, _ = repository.get(session, repository.Entities.USUARIO, {'email': email}, first=True)
    if not db_usuario:
        raise ValueError('Não foi encontrado usuário com esse email')

    nova_senha = random.randint(int('1'*9), int('9'*9))
    db_usuario.senha = nova_senha
    session.commit()

    send_email.enviar(
        assunto='KDerninho - Recuperar Senha',
        corpo=f'Sua nova senha temporária é {nova_senha}',
        para=[db_usuario.email]
    )
    return render(request, 'autenticacao/login.html', context={'message': f'Senha enviada para: {db_usuario.email}', 'error': error, 'data_bs_theme': 'auto'})


@app.exception_handler(IntegrityError)
async def integrity_error_exception_handler(request: fastapi.Request, ex, redirect_to: str = None):
    logger.exception(ex)
    if not redirect_to:
        redirect_to = str(request.headers.get('referer', request.url_for('get_app_index')))

    error = f'<span>Verifique os campos preenchidos'
    detalhe = re.search(r'\.(\w+)$', str(ex.orig))
    if detalhe:
        detalhe = detalhe.group(1)
        error = f'<span>Campo&nbsp;<code>{detalhe}</code>&nbsp;inválido'

    redirect_to = url_incluir_query_params(redirect_to, error=error)
    return fastapi.responses.RedirectResponse(redirect_to, status_code=302)


@app.exception_handler(ValueError)
async def value_error_exception_handler(request: fastapi.Request, ex, redirect_to: str = None):
    if not isinstance(ex, HTTPException):
        logger.exception(ex)
    if not redirect_to:
        redirect_to = str(request.headers.get('referer', request.url_for('get_app_index')))
    redirect_to = url_incluir_query_params(redirect_to, error=str(ex))
    return fastapi.responses.RedirectResponse(redirect_to, status_code=302)


@app.exception_handler(HTTPException)
async def http_error_exception_handler(request: fastapi.Request, ex: HTTPException):
    if ex.status_code == 401:
        request.session.clear()
        redirect_to = request.url_for('get_app_index')
        logger.warning('Não autorizado')
    else:
        logger.exception(ex)
        redirect_to = str(request.headers.get('referer', request.url_for('get_app_index')))
    return await value_error_exception_handler(request, ex, redirect_to=redirect_to)


@app.exception_handler(RequestValidationError)
async def generic_exception_handler(request: fastapi.Request, ex: Exception):
    logger.exception(ex)
    redirect_to = str(request.headers.get('referer', request.url_for('get_app_index')))
    redirect_to = url_incluir_query_params(redirect_to, error=ex.errors()[0]["msg"])
    return fastapi.responses.RedirectResponse(redirect_to, status_code=302)
