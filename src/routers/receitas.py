from typing import List

from fastapi import Body, Depends
from fastapi.routing import APIRouter
from sqlmodel import Session

from db import get_session
from domain.entities import Receita, ReceitaIngredienteLink

router = APIRouter(
    prefix='/receitas'
)


@router.post('/')
async def criar_receita(nome: str = Body(), peso_unitario: int = Body(), ingredientes: List[ReceitaIngredienteLink] = Body([]), session: Session = Depends(get_session)) -> Receita:
    receita = Receita(
        nome=nome,
        peso_unitario=peso_unitario
    )
    for ingrediente in ingredientes:
        receita_ingrediente = ReceitaIngredienteLink(
            quantidade=ingrediente.quantidade,
            ingrediente_id=ingrediente.ingrediente_id,
            receita_id=receita.id
        )
        session.add(receita_ingrediente)
    session.commit()
    return receita
