import logging
import re
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import fastapi
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from sqlalchemy.log import rootlogger
from starlette.middleware.trustedhost import TrustedHostMiddleware

from src import db
from src.domain import inputs, repository
from src.routers.autenticacao import router as router_autenticacao
from src.routers.estoques import router as router_estoques
from src.routers.ingredientes import router as router_ingredientes
from src.routers.organizacao import router as router_organizacao
from src.routers.paginas import router as router_paginas
from src.routers.receitas import router as router_receitas
from src.routers.scripts import router as router_scripts
from src.routers.vendas import router as router_vendas
from src.templates import render
from src.utils import redirect_back

rootlogger.setLevel(logging.WARN)

app = fastapi.FastAPI()
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

app.include_router(router_receitas)
app.include_router(router_ingredientes)
app.include_router(router_estoques)
app.include_router(router_vendas)
app.include_router(router_organizacao)
app.include_router(router_scripts)
app.include_router(router_autenticacao)
app.include_router(router_paginas)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

db.init()


@app.get('/', include_in_schema=False)
async def get_index(request: fastapi.Request, message: str = fastapi.Query(None),  error: str = fastapi.Query(None)):
    return render(request, 'autenticacao/login.html', context={'message': message, 'error': error, 'data_bs_theme': 'auto'})


@app.get('/registrar', include_in_schema=False)
async def get_registrar(request: fastapi.Request, message: str = fastapi.Query(None),  error: str = fastapi.Query(None)):
    return render(request, 'autenticacao/criar_conta.html', context={'message': message, 'error': error, 'data_bs_theme': 'auto'})


@app.post('/registrar', include_in_schema=False)
async def post_registrar(request: fastapi.Request, payload: inputs.UsuarioCriar = fastapi.Form(), error: str = fastapi.Query(None), session: db.Session = db.SESSION_DEP):
    template_name = 'autenticacao/login.html'
    message = None
    try:
        if payload.senha != payload.senha_confirmar:
            raise Exception('As senhas não batem')

        repository.create_usuario(session, nome=payload.nome, email=payload.email, senha=payload.senha, organizacao_descricao=payload.organizacao_descricao, dono=True)
        message = 'Conta criada com sucesso'
    except Exception as ex:
        template_name = 'autenticacao/criar_conta.html'
        error = str(ex)

    return render(request, template_name, context={'error': error, 'message': message, 'data_bs_theme': 'auto'})


@app.get('/recuperar_senha', include_in_schema=False)
async def get_recuperar_senha(request: fastapi.Request, message: str = fastapi.Query(None),  error: str = fastapi.Query(None)):
    return render(request, 'autenticacao/recuperar_senha.html', context={'message': message, 'error': error, 'data_bs_theme': 'auto'})


@app.post('/recuperar_senha', include_in_schema=False)
async def post_recuperar_senha(request: fastapi.Request, email: str = fastapi.Form(), message: str = fastapi.Query(None),  error: str = fastapi.Query(None)):
    return render(request, 'autenticacao/login.html', context={'message': f'Senha enviada para: {email}', 'error': error, 'data_bs_theme': 'auto'})


@app.post('/alterar_senha', include_in_schema=False)
async def post_alterar_senha(request: fastapi.Request, payload: inputs.AlterarSenha = fastapi.Form(),  session: db.Session = db.SESSION_DEP):
    repository.update_usuario_senha(session, id=payload.id, senha_atual=payload.senha_atual, senha=payload.senha, senha_confirmar=payload.senha_confirmar)
    return redirect_back(request)


@app.exception_handler(IntegrityError)
async def integrity_error_exception_handler(request: fastapi.Request, ex, redirect_to: str = None):
    if not redirect_to:
        redirect_to = str(request.headers.get('referer', request.url_for('get_index')))

    parsed_url = urlparse(url=str(redirect_to))

    query_params = parse_qs(parsed_url.query)

    detalhe = re.search(r'\.(\w+)$', str(ex.orig))
    if detalhe:
        detalhe = detalhe.group(1)
        query_params['error'] = f'<b>{parsed_url.path}</b>&nbsp;-&nbsp;<span>Campo&nbsp;<code>{detalhe}</code>&nbsp;inválido'
    else:
        query_params['error'] = f'<b>{parsed_url.path}</b>&nbsp;-&nbsp;<span>Verifique os campos preenchidos'

    new_query = urlencode(query_params, doseq=True)
    parsed_url = parsed_url._replace(query=new_query)
    redirect_to = urlunparse(parsed_url)

    return fastapi.responses.RedirectResponse(redirect_to, status_code=302)


@app.exception_handler(ValueError)
async def integrity_error_exception_handler(request: fastapi.Request, ex, redirect_to: str = None):
    if not redirect_to:
        redirect_to = str(request.headers.get('referer', request.url_for('get_index')))

    parsed_url = urlparse(url=str(redirect_to))

    query_params = parse_qs(parsed_url.query)

    query_params['error'] = str(ex)

    new_query = urlencode(query_params, doseq=True)
    parsed_url = parsed_url._replace(query=new_query)

    redirect_to = urlunparse(parsed_url)

    return fastapi.responses.RedirectResponse(redirect_to, status_code=302)


@app.exception_handler(HTTPException)
async def http_error_exception_handler(request: fastapi.Request, ex: HTTPException):
    redirect_to = str(request.headers.get('referer', request.url_for('get_index')))
    if ex.status_code == 401:
        redirect_to = request.url_for('get_index')

    return await integrity_error_exception_handler(request, ex, redirect_to=redirect_to)


@app.exception_handler(RequestValidationError)
async def generic_exception_handler(request: fastapi.Request, ex: Exception):
    redirect_to = str(request.headers.get('referer', request.url_for('get_index')))

    parsed_url = urlparse(url=str(redirect_to))

    query_params = parse_qs(parsed_url.query)

    query_params['error'] = ex.errors()[0]["msg"]

    new_query = urlencode(query_params, doseq=True)
    parsed_url = parsed_url._replace(query=new_query)

    redirect_to = urlunparse(parsed_url)

    return fastapi.responses.RedirectResponse(redirect_to, status_code=302)
