from typing import List

from sqlmodel import Session, select

from domain.entities import Ingrediente, Receita, ReceitaIngredienteLink


def get_receitas(session: Session) -> List[Receita]:
    receitas = session.exec(select(Receita)).all()
    return receitas


def get_receita(session: Session, id: int) -> Receita:
    receita = session.get(Receita, id)
    return receita


def update_receita(session: Session, id: int, nome: str, peso_unitario: float, porcentagem_lucro: float) -> Receita:
    db_receita = get_receita(session, id)
    db_receita.nome = nome
    db_receita.peso_unitario = peso_unitario
    db_receita.porcentagem_lucro = porcentagem_lucro
    session.commit()
    return db_receita


def get_ingredientes(session: Session) -> List[Ingrediente]:
    ingredientes = session.exec(select(Ingrediente)).all()
    return ingredientes


def create_receita_ingrediente(session: Session, receita_id: int, ingrediente_id: int, quantidade: float) -> ReceitaIngredienteLink:
    receita_ingrediente = ReceitaIngredienteLink(
        receita_id=receita_id,
        ingrediente_id=ingrediente_id,
        quantidade=quantidade
    )
    session.add(receita_ingrediente)
    session.commit()
    return receita_ingrediente


def delete_receita_ingrediente(session: Session, receita_ingrediente_id: int) -> bool:
    receita_ingrediente = session.get(ReceitaIngredienteLink, receita_ingrediente_id)
    session.delete(receita_ingrediente)
    session.commit()
    return True
