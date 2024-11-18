import logging
import re
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import fastapi
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from sqlalchemy.log import rootlogger
from starlette.middleware.trustedhost import TrustedHostMiddleware

from src import auth, db
from src.domain import inputs, repository
from src.routers.estoques import router as router_estoques
from src.routers.ingredientes import router as router_ingredientes
from src.routers.receitas import router as router_receitas
from src.routers.vendas import router as router_vendas
from src.scripts import seed
from src.templates import render
from src.utils import redirect_back

rootlogger.setLevel(logging.WARN)

app = fastapi.FastAPI()
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

app.include_router(router_receitas)
app.include_router(router_ingredientes)
app.include_router(router_estoques)
app.include_router(router_vendas)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

db.init()


@app.get('/', include_in_schema=False)
async def get_index(request: fastapi.Request, message: str = fastapi.Query(None)):
    return render(request, 'login.html', context={'message': message, 'data_bs_theme': 'auto'})


@app.post('/authenticate')
async def post_authenticate(email: str = fastapi.Form(), senha: str = fastapi.Form(), session: db.Session = db.SESSION_DEP):
    return auth.authenticate(session, email=email, senha=senha)


@app.post('/login', include_in_schema=False)
async def post_login(request: fastapi.Request, email: str = fastapi.Form(), senha: str = fastapi.Form(), session: db.Session = db.SESSION_DEP):
    return auth.request_login(session, request, email=email, senha=senha)


@app.get('/logout', include_in_schema=False)
async def get_logout(request: fastapi.Request):
    return auth.request_logout(request)


@app.get('/home', include_in_schema=False, dependencies=[auth.HEADER_AUTH])
async def get_home(request: fastapi.Request, session: db.Session = db.SESSION_DEP):
    db_receitas = repository.list_receitas(session)
    db_ingredientes = repository.get_ingredientes(session)
    db_estoques = repository.list_estoques(session)
    db_vendas = repository.list_vendas(session)

    return render(request, 'home.html', session, context={
        'len_receitas': len(db_receitas),
        'len_ingredientes': len(db_ingredientes),
        'estoques': len(db_estoques),
        'vendas': len(db_vendas),
    })


@app.get('/sobre', include_in_schema=False, dependencies=[auth.HEADER_AUTH])
async def get_sobre(request: fastapi.Request, session: db.Session = db.SESSION_DEP):
    return render(request, 'sobre.html', session)


@app.post('/perfil', dependencies=[auth.HEADER_AUTH])
async def post_perfil(request: fastapi.Request, payload: inputs.UsuarioAtualizar,  session: db.Session = db.SESSION_DEP):
    repository.update_usuario(session, id=payload.id, nome=payload.nome, email=payload.email)
    return redirect_back(request)


@app.post('/scripts/seed', tags=['Scripts'])
async def post_scripts_seed(Authorization: str = fastapi.Header(None)):
    if not Authorization == 'batatafrita':
        raise fastapi.HTTPException(401, 'Não autorizado')
    seed.main()
    return True


@app.post('/scripts/reset_db', tags=['Scripts'])
async def post_scripts_reset_db(Authorization: str = fastapi.Header(None)):
    if not Authorization == 'batatafrita':
        raise fastapi.HTTPException(401, 'Não autorizado')
    db.reset()
    seed.main()
    return True


@app.exception_handler(IntegrityError)
async def integrity_error_exception_handler(req: fastapi.Request, ex):
    parsed_url = urlparse(req.headers['referer'])
    query_params = parse_qs(parsed_url.query)

    detalhe = re.search(r'\.(\w+)$', str(ex.orig))
    if detalhe:
        detalhe = detalhe.group(1)
        query_params['error'] = f'&nbsp;&nbsp;<b>{parsed_url.path}</b>&nbsp;-&nbsp;<span>Campo&nbsp;<code>{detalhe}</code>&nbsp;inválido</span>'
    else:
        query_params['error'] = f'&nbsp;&nbsp;<b>{parsed_url.path}</b>&nbsp;-&nbsp;<span>Verifique os campos preenchidos</span>'

    new_query = urlencode(query_params, doseq=True)
    parsed_url = parsed_url._replace(query=new_query)
    url = urlunparse(parsed_url)

    return fastapi.responses.RedirectResponse(url, status_code=302)


@app.exception_handler(ValueError)
async def integrity_error_exception_handler(request: fastapi.Request, ex):
    url = str(request.headers['referer'])
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    query_params['error'] = f'&nbsp;&nbsp;<span>{ex}</span>'

    new_query = urlencode(query_params, doseq=True)
    parsed_url = parsed_url._replace(query=new_query)

    url = urlunparse(parsed_url)

    return fastapi.responses.RedirectResponse(url, status_code=302)


@app.exception_handler(HTTPException)
async def http_error_exception_handler(request: fastapi.Request, ex: HTTPException):
    return await integrity_error_exception_handler(request, ex)
