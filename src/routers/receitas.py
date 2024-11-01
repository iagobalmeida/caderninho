from fastapi import Form, Request
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from db import SESSION_DEP
from domain import repository

router = APIRouter(prefix='/receitas')
templates = Jinja2Templates(directory='src/templates')


@router.get('/')
async def get_receitas_index(request: Request):
    return RedirectResponse(request.url_for('get_index'), status_code=302)


@router.post('/')
async def post_receitas_index(request: Request, nome: str = Form(), session: Session = SESSION_DEP):
    nova_receita = repository.create_receita(session, nome)
    return RedirectResponse(request.url_for('get_receita', id=nova_receita.id), status_code=302)


@router.get('/{id}')
async def get_receita(request: Request, id: int, session: Session = SESSION_DEP):
    db_receita = repository.get_receita(session, id)
    db_ingredientes = repository.get_ingredientes(session)
    return templates.TemplateResponse(
        request=request,
        name='receitas/detail.html',
        context={
            'receita': db_receita.dict(),
            'ingredientes': db_ingredientes
        }
    )


@router.post('/{id}/atualizar')
async def post_receita_atualizar(request: Request, id: int, nome: str = Form(), peso_unitario: float = Form(), porcentagem_lucro: float = Form(), session: Session = SESSION_DEP):
    repository.update_receita(
        session,
        id=id,
        nome=nome,
        peso_unitario=peso_unitario,
        porcentagem_lucro=porcentagem_lucro
    )
    return RedirectResponse(request.url_for('get_receita', id=id), status_code=302)


@router.post('/{id}/deletar')
async def post_receita_deletar(request: Request, id: int, nome: str = Form(), peso_unitario: float = Form(), porcentagem_lucro: float = Form(), session: Session = SESSION_DEP):
    repository.delete_receita(
        session,
        id=id
    )
    return RedirectResponse(request.url_for('get_index'), status_code=302)


@router.post('/{id}/ingredientes/adicionar')
async def post_receita_ingredientes_adicionar(request: Request, id: int, ingrediente_id: int = Form(), quantidade: float = Form(), session: Session = SESSION_DEP):
    repository.create_receita_ingrediente(
        session,
        receita_id=id,
        ingrediente_id=ingrediente_id,
        quantidade=quantidade
    )
    return RedirectResponse(request.url_for('get_receita', id=id), status_code=302)


@router.post('/{receita_id}/ingredientes/atualizar')
async def post_receita_ingredientes_atualizar(request: Request, receita_id: int, id: int = Form(), quantidade: float = Form(), session: Session = SESSION_DEP):
    repository.update_receita_ingrediente(
        session,
        id=id,
        quantidade=quantidade
    )
    return RedirectResponse(request.url_for('get_receita', id=receita_id), status_code=302)


@router.post('/{receita_id}/ingredientes/remover')
async def post_receita_ingredientes_remover(request: Request, receita_id: int, id: int = Form(), session: Session = SESSION_DEP):
    repository.delete_receita_ingrediente(session, id)
    return RedirectResponse(request.url_for('get_receita', id=receita_id), status_code=302)
