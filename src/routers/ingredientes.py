from typing import List

from fastapi import Depends
from fastapi.routing import APIRouter
from sqlmodel import Session, select

from db import get_session
from domain.entities import Ingrediente

router = APIRouter(
    prefix='/ingredientes'
)


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
