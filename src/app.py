import logging
import re

from fastapi import FastAPI, Form, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from sqlalchemy.log import rootlogger
from sqlmodel import Session

from db import SESSION_DEP, init
from domain import repository
from routers.ingredientes import router as router_ingredientes
from routers.receitas import router as router_receitas
from scripts import seed

rootlogger.setLevel(logging.WARN)

app = FastAPI()
app.include_router(router_receitas)
app.include_router(router_ingredientes)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

templates = Jinja2Templates(directory='src/templates')

init()


@app.get('/')
async def get_index(request: Request, session: Session = SESSION_DEP):
    db_receitas = repository.get_receitas(session)
    db_receitas = [r.dict() for r in db_receitas]
    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={
            'receitas': db_receitas
        }
    )


@app.get('/{id}')
async def get_receita(request: Request, id: int, session: Session = SESSION_DEP):
    db_receita = repository.get_receita(session, id)
    db_receita = db_receita.dict()

    db_ingredientes = repository.get_ingredientes(session)

    custo_total = sum([i.custo for i in db_receita['ingredientes']])
    quantidade_total = max(1, sum([i.quantidade for i in db_receita['ingredientes']]))
    custo_p_grama_total = round(custo_total/quantidade_total, 2)

    return templates.TemplateResponse(
        request=request,
        name='receita.html',
        context={
            **db_receita,
            'ingredientes': db_ingredientes,
            'receita_ingredientes': [
                *db_receita['ingredientes'],
                {
                    'ingrediente_id': -1,
                    'ingrediente': {
                        'nome': 'Total',
                        'custo_p_grama': custo_p_grama_total,
                    },
                    'quantidade': quantidade_total,
                    'custo': custo_total
                }
            ],
        }
    )


@app.post('/{id}/atualizar')
async def post_receita_atualizar(request: Request, id: int, nome: str = Form(), peso_unitario: float = Form(), porcentagem_lucro: float = Form(), session: Session = SESSION_DEP):
    repository.update_receita(
        session,
        id=id,
        nome=nome,
        peso_unitario=peso_unitario,
        porcentagem_lucro=porcentagem_lucro
    )
    return RedirectResponse(request.url_for('get_receita', id=id), status_code=302)


@app.post('/{id}/ingredientes/adicionar')
async def post_receita_ingredientes_adicionar(request: Request, id: int, ingrediente_id: int = Form(), quantidade: float = Form(), session: Session = SESSION_DEP):
    repository.create_receita_ingrediente(
        session,
        receita_id=id,
        ingrediente_id=ingrediente_id,
        quantidade=quantidade
    )
    return RedirectResponse(request.url_for('get_receita', id=id), status_code=302)


@app.get('/{id}/ingredientes/remover/{receita_ingrediente_id}')
async def post_receita_ingredientes_remover(request: Request, id: int, receita_ingrediente_id: int, session: Session = SESSION_DEP):
    repository.delete_receita_ingrediente(session, receita_ingrediente_id)
    return RedirectResponse(request.url_for('get_receita', id=id), status_code=302)


@app.post('/seed')
async def post_seed():
    seed.main()
    return True


@app.exception_handler(IntegrityError)
async def integrity_error_exception_handler(req, ex):
    detalhe = re.search(r'\.(\w+)$', str(ex.orig))
    if detalhe:
        detalhe = detalhe.group(1)
        raise HTTPException(status_code=422, detail=f'Campo "{detalhe}" inválido')
    raise HTTPException(status_code=422, detail='Verifique os campos preenchidos')
