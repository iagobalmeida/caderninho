from datetime import datetime
from typing import List, Tuple

from sqlmodel import Session, func, select

from domain.entities import (Estoque, Ingrediente, Receita,
                             ReceitaIngredienteLink, Venda)


def create_receita(session: Session, nome: str) -> Receita:
    receita = Receita(
        nome=nome,
        peso_unitario=1,
        porcentagem_lucro=33
    )
    session.add(receita)
    session.commit()
    return receita


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


def delete_receita(session: Session, id: int) -> bool:
    receita = get_receita(session, id)
    session.delete(receita)
    session.commit()
    return True


def get_ingredientes(session: Session) -> List[Ingrediente]:
    ingredientes = session.exec(select(Ingrediente)).all()
    return ingredientes


def get_ingrediente(session: Session, id: int) -> Ingrediente:
    ingrediente = session.get(Ingrediente, id)
    return ingrediente


def update_ingrediente(session: Session, id: int, nome: str, peso: float, custo: float) -> Ingrediente:
    db_ingrediente = get_ingrediente(session, id)
    db_ingrediente.nome = nome
    db_ingrediente.peso = peso
    db_ingrediente.custo = custo
    session.commit()
    return db_ingrediente


def create_ingrediente(session: Session, nome: str, peso: float, custo: float) -> Ingrediente:
    novo_ingrediente = Ingrediente(
        nome=nome,
        peso=peso,
        custo=custo
    )
    session.add(novo_ingrediente)
    session.commit()
    return novo_ingrediente


def create_receita_ingrediente(session: Session, receita_id: int, ingrediente_id: int, quantidade: float) -> ReceitaIngredienteLink:
    receita_ingrediente = ReceitaIngredienteLink(
        receita_id=receita_id,
        ingrediente_id=ingrediente_id,
        quantidade=quantidade
    )
    session.add(receita_ingrediente)
    session.commit()
    return receita_ingrediente


def update_receita_ingrediente(session: Session, id: int, quantidade: float) -> ReceitaIngredienteLink:
    receita_ingrediente = session.get(ReceitaIngredienteLink, id)
    receita_ingrediente.quantidade = quantidade
    session.commit()
    return receita_ingrediente


def delete_receita_ingrediente(session: Session, receita_ingrediente_id: int) -> bool:
    receita_ingrediente = session.get(ReceitaIngredienteLink, receita_ingrediente_id)
    session.delete(receita_ingrediente)
    session.commit()
    return True


def delete_ingrediente(session: Session, id: int) -> bool:
    links_receitas = session.exec(select(ReceitaIngredienteLink).where(ReceitaIngredienteLink.ingrediente_id == id)).all()
    for link in links_receitas:
        session.delete(link)
    ingrediente = session.get(Ingrediente, id)
    session.delete(ingrediente)
    session.commit()
    return True


def list_estoques(session: Session, filter_ingrediente_id: int = -1, filter_data_inicio: datetime = None, filter_data_final: datetime = None) -> List[Estoque]:
    query = select(Estoque)

    if filter_ingrediente_id and filter_ingrediente_id != -1:
        query = query.filter(Estoque.ingrediente_id == filter_ingrediente_id)

    if filter_data_inicio:
        query = query.filter(Estoque.data_criacao >= filter_data_inicio)

    if filter_data_final:
        query = query.filter(Estoque.data_criacao >= filter_data_final)

    query = query.order_by(Estoque.data_criacao.desc())

    return session.exec(query).all()


def get_vendas(session: Session) -> List[Venda]:
    ret = session.exec(select(Venda).order_by(Venda.data_criacao.desc())).all()
    return ret


def get_fluxo_caixa(session: Session) -> Tuple[float, float, float]:
    entradas = session.exec(select(func.sum(Venda.valor))).first()
    saidas = session.exec(select(func.sum(Estoque.valor_pago))).first()
    caixa = entradas - saidas
    return (entradas, saidas, caixa)
