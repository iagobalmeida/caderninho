import logging
import re
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from sqlalchemy.log import rootlogger

from db import SESSION_DEP, Session, init
from domain import repository
from routers.estoques import router as router_estoques
from routers.ingredientes import router as router_ingredientes
from routers.receitas import router as router_receitas
from routers.vendas import router as router_vendas
from scripts import seed
from templates import render

rootlogger.setLevel(logging.WARN)

app = FastAPI()
app.include_router(router_receitas)
app.include_router(router_ingredientes)
app.include_router(router_estoques)
app.include_router(router_vendas)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

init()


@app.get('/')
async def get_index(request: Request, session: Session = SESSION_DEP):
    db_receitas = repository.list_receitas(session)
    db_ingredientes = repository.get_ingredientes(session)
    db_estoques = repository.list_estoques(session)
    db_vendas = repository.list_vendas(session)

    entradas, saidas, caixa = repository.get_fluxo_caixa(session)

    return render(request, 'index.html', {
        'receitas': len(db_receitas),
        'ingredientes': len(db_ingredientes),
        'estoques': len(db_estoques),
        'vendas': len(db_vendas),
        'entradas': entradas,
        'saidas': saidas,
        'caixa': caixa
    })


@app.post('/seed')
async def post_seed():
    seed.main()
    return True


@app.exception_handler(IntegrityError)
async def integrity_error_exception_handler(req: Request, ex):
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

    return RedirectResponse(url, status_code=302)


@app.exception_handler(ValueError)
async def integrity_error_exception_handler(req: Request, ex):
    url = str(req.url_for('get_index'))
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    query_params['error'] = f'&nbsp;&nbsp;<span>{ex}</span>'

    new_query = urlencode(query_params, doseq=True)
    parsed_url = parsed_url._replace(query=new_query)

    url = urlunparse(parsed_url)

    return RedirectResponse(url, status_code=302)
