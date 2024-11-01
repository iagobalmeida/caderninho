import logging
import re

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from sqlalchemy.log import rootlogger

from db import SESSION_DEP, Session, init
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

    db_ingredientes = repository.get_ingredientes(session)
    db_ingredientes = [i for i in db_ingredientes]

    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={
            'receitas': db_receitas,
            'ingredientes': db_ingredientes
        }
    )


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
