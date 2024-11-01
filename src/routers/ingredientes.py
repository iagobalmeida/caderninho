from typing import List

from fastapi import Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter
from sqlmodel import Session, select

from db import SESSION_DEP, get_session
from domain import repository
from domain.entities import Ingrediente

router = APIRouter(
    prefix='/ingredientes'
)


@router.post('/')
async def post_ingredientes_index(request: Request, nome: str = Form(), peso: float = Form(), custo: float = Form(), session: Session = SESSION_DEP):
    repository.create_ingrediente(
        session,
        nome=nome,
        peso=peso,
        custo=custo
    )
    return RedirectResponse(request.url_for('get_index'), status_code=302)


@router.post('/editar')
async def post_ingredientes_editar(request: Request, id: int = Form(),  nome: str = Form(), peso: float = Form(), custo: float = Form(), session: Session = SESSION_DEP):
    repository.update_ingrediente(
        session,
        id=id,
        nome=nome,
        peso=peso,
        custo=custo
    )
    return RedirectResponse(request.url_for('get_index'), status_code=302)


@router.post('/excluir')
async def post_ingredientes_excluir(request: Request, id: int = Form(), session: Session = SESSION_DEP):
    repository.delete_ingrediente(
        session,
        id=id
    )
    return RedirectResponse(request.url_for('get_index'), status_code=302)


@router.get('/')
async def get_ingredientes(session: Session = Depends(get_session)) -> List[Ingrediente]:
    return session.exec(select(Ingrediente)).all()


@router.post('/')
async def criar_ingrediente(ingrediente: Ingrediente, session: Session = Depends(get_session)) -> Ingrediente:
    try:
        session.add(ingrediente)
        session.commit()
        return ingrediente
    except Exception as ex:
        session.rollback()
        raise ex
