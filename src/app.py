import logging
import re
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import fastapi
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from sqlalchemy.log import rootlogger

import auth
from db import SESSION_DEP, Session, init
from domain import repository
from routers.estoques import router as router_estoques
from routers.ingredientes import router as router_ingredientes
from routers.receitas import router as router_receitas
from routers.vendas import router as router_vendas
from scripts import seed
from templates import render
from utils import redirect_url_for

rootlogger.setLevel(logging.WARN)

app = fastapi.FastAPI(dependencies=[auth.AUTH_DEP])
app.include_router(router_receitas)
app.include_router(router_ingredientes)
app.include_router(router_estoques)
app.include_router(router_vendas)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

init()


@app.get('/', include_in_schema=False)
async def get_index(request: fastapi.Request, message: str = fastapi.Query(None), session: Session = SESSION_DEP):
    return render(session, request, 'login.html', {'message': message})


@app.post('/login', include_in_schema=False)
async def post_login(request: fastapi.Request, email: str = fastapi.Form(), senha: str = fastapi.Form(), session: Session = SESSION_DEP):
    jwt_token = auth.authenticate(session, email=email, senha=senha)
    if jwt_token:
        response = redirect_url_for(request, 'get_home')
        response.set_cookie('jwt_token', jwt_token)
    else:
        url = request.url_for('get_index')
        url = url.include_query_params(message='Email e/ou senha inválidos!')
        response = fastapi.responses.RedirectResponse(url, status_code=302)
        response.delete_cookie('jwt_token')
    return response


@app.get('/logout', include_in_schema=False)
async def get_logout(request: fastapi.Request):
    response = redirect_url_for(request, 'get_index')
    response.delete_cookie('jwt_token')
    return response


@app.get('/home', include_in_schema=False)
async def get_home(request: fastapi.Request, session: Session = SESSION_DEP):
    db_receitas = repository.list_receitas(session)
    db_ingredientes = repository.get_ingredientes(session)
    db_estoques = repository.list_estoques(session)
    db_vendas = repository.list_vendas(session)

    return render(session, request, 'home.html', {
        'receitas': len(db_receitas),
        'len_ingredientes': len(db_ingredientes),
        'estoques': len(db_estoques),
        'vendas': len(db_vendas),
    })


@app.post('/seed')
async def post_seed():
    seed.main()
    return True


@app.exception_handler(IntegrityError)
async def integrity_error_exception_handler(req: fastapi.Request, ex):
    parsed_url = urlparse(req.headers['referer'])
    query_params = parse_qs(parsed_url.query)

    detalhe = re.search(r'\.(\w+)$', str(ex.orig))
    detalhe = detalhe.group(1)
    if detalhe:
        query_params['error'] = f'&nbsp;&nbsp;<b>{parsed_url.path}</b>&nbsp;-&nbsp;<span>Campo&nbsp;<code>{detalhe}</code>&nbsp;inválido</span>'
    else:
        query_params['error'] = f'&nbsp;&nbsp;<b>{parsed_url.path}</b>&nbsp;-&nbsp;<span>Verifique os campos preenchidos</span>'

    new_query = urlencode(query_params, doseq=True)
    parsed_url = parsed_url._replace(query=new_query)
    url = urlunparse(parsed_url)

    return fastapi.responses.RedirectResponse(url, status_code=302)


@app.exception_handler(ValueError)
async def integrity_error_exception_handler(req: fastapi.Request, ex):
    url = str(req.url_for('get_home'))
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    query_params['error'] = f'&nbsp;&nbsp;<span>{ex}</span>'

    new_query = urlencode(query_params, doseq=True)
    parsed_url = parsed_url._replace(query=new_query)

    url = urlunparse(parsed_url)

    return fastapi.responses.RedirectResponse(url, status_code=302)
