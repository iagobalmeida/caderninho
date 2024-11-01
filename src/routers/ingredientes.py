from fastapi import Form, Request
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter
from sqlmodel import Session

from db import SESSION_DEP
from domain import repository
from templates import templates

router = APIRouter(
    prefix='/ingredientes'
)


@router.get('/')
async def get_ingredientes_index(request: Request, session: Session = SESSION_DEP):
    db_ingredientes = repository.get_ingredientes(session)
    return templates.TemplateResponse(
        request=request,
        name='ingredientes/list.html',
        context={
            'ingredientes': db_ingredientes
        }
    )


@router.post('/')
async def post_ingredientes_index(request: Request, nome: str = Form(), peso: float = Form(), custo: float = Form(), session: Session = SESSION_DEP):
    repository.create_ingrediente(
        session,
        nome=nome,
        peso=peso,
        custo=custo
    )
    return RedirectResponse(request.headers['referer'], status_code=302)


@router.post('/editar')
async def post_ingredientes_editar(request: Request, id: int = Form(),  nome: str = Form(), peso: float = Form(), custo: float = Form(), session: Session = SESSION_DEP):
    repository.update_ingrediente(
        session,
        id=id,
        nome=nome,
        peso=peso,
        custo=custo
    )
    return RedirectResponse(request.headers['referer'], status_code=302)


@router.post('/excluir')
async def post_ingredientes_excluir(request: Request, id: int = Form(), session: Session = SESSION_DEP):
    repository.delete_ingrediente(
        session,
        id=id
    )
    return RedirectResponse(request.headers['referer'], status_code=302)
