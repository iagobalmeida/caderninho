from datetime import datetime
from typing import List, Tuple

from sqlmodel import Session, SQLModel, func, select

from domain.entities import (Estoque, Ingrediente, Receita,
                             ReceitaIngredienteLink, Venda)


def __delete(session: Session, entity: SQLModel, id: int) -> bool:
    db_entity = session.get(entity, id)
    if not db_entity:
        return True
    session.delete(db_entity)
    session.commit()
    return True


def delete_receita(session: Session, id: int) -> bool:
    return __delete(session, Receita, id)


def delete_receita_ingrediente(session: Session, receita_ingrediente_id: int) -> bool:
    return __delete(session, ReceitaIngredienteLink, receita_ingrediente_id)


def delete_venda(session: Session, id: int) -> bool:
    return __delete(session, Venda, id)


def delete_ingrediente(session: Session, id: int) -> bool:
    links_receitas = session.exec(select(ReceitaIngredienteLink).where(ReceitaIngredienteLink.ingrediente_id == id)).all()
    for link in links_receitas:
        session.delete(link)
    return __delete(session, Ingrediente, id)


def __update(session: Session, entity: SQLModel, id: int, **kwargs) -> SQLModel:
    db_entity = session.get(entity, id)
    for key, value in kwargs.items():
        db_entity.__setattr__(key, value)
    session.commit()
    return db_entity


def update_receita(session: Session, id: int, nome: str, peso_unitario: float, porcentagem_lucro: float) -> Receita:
    return __update(session, Receita, id, nome=nome, peso_unitario=peso_unitario, porcentagem_lucro=porcentagem_lucro)


def update_ingrediente(session: Session, id: int, nome: str, peso: float, custo: float) -> Ingrediente:
    return __update(session, Ingrediente, id, nome=nome, peso=peso, custo=custo)


def update_receita_ingrediente(session: Session, id: int, quantidade: float) -> ReceitaIngredienteLink:
    return __update(session, ReceitaIngredienteLink, id, quantidade=quantidade)


def update_venda(session: Session, id: int, descricao: str, valor: float) -> Venda:
    return __update(session, Venda, id, descricao=descricao, valor=valor)


def __create(session: Session, entity):
    session.add(entity)
    session.commit()
    return entity


def create_receita(session: Session, nome: str) -> Receita:
    return __create(session, Receita(nome=nome, peso_unitario=1, porcentagem_lucro=33))


def list_receitas(session: Session, filter_nome: str = None) -> List[Receita]:
    query = select(Receita)
    if filter_nome:
        query = query.filter(Receita.nome.like(f'%{filter_nome}%'))
    receitas = session.exec(query).all()
    return receitas


def get_receita(session: Session, id: int) -> Receita:
    receita = session.get(Receita, id)
    return receita


def get_ingredientes(session: Session) -> List[Ingrediente]:
    ingredientes = session.exec(select(Ingrediente)).all()
    return ingredientes


def create_ingrediente(session: Session, nome: str, peso: float, custo: float) -> Ingrediente:
    novo_ingrediente = Ingrediente(
        nome=nome,
        peso=peso,
        custo=custo
    )
    session.add(novo_ingrediente)
    session.commit()
    return novo_ingrediente


def create_receita_ingrediente(session: Session, id: int, ingrediente_id: int, quantidade: float) -> ReceitaIngredienteLink:
    receita_ingrediente = ReceitaIngredienteLink(
        receita_id=id,
        ingrediente_id=ingrediente_id,
        quantidade=quantidade
    )
    session.add(receita_ingrediente)
    session.commit()
    return receita_ingrediente


def list_estoques(session: Session, filter_ingrediente_id: int = -1, filter_data_inicio: datetime = None, filter_data_final: datetime = None) -> List[Estoque]:
    query = select(Estoque)

    if filter_ingrediente_id and filter_ingrediente_id != -1:
        query = query.filter(Estoque.ingrediente_id == filter_ingrediente_id)

    if filter_data_inicio:
        query = query.filter(Estoque.data_criacao >= filter_data_inicio)

    if filter_data_final:
        query = query.filter(Estoque.data_criacao <= filter_data_final)

    query = query.order_by(Estoque.data_criacao.desc())

    return session.exec(query).all()


def list_vendas(session: Session, filter_data_inicio: datetime = None, filter_data_final: datetime = None) -> List[Venda]:
    query = select(Venda)

    if filter_data_inicio:
        query = query.filter(Venda.data_criacao >= filter_data_inicio)

    if filter_data_final:
        query = query.filter(Venda.data_criacao <= filter_data_final)

    ret = session.exec(query.order_by(Venda.data_criacao.desc())).all()
    return ret


def create_venda(session: Session, descricao: str, valor: float) -> Venda:
    venda = Venda(
        descricao=descricao,
        valor=valor
    )
    session.add(venda)
    session.commit()
    return venda


def get_fluxo_caixa(session: Session) -> Tuple[float, float, float]:
    entradas = session.exec(select(func.sum(Venda.valor))).first()
    saidas = session.exec(select(func.sum(Estoque.valor_pago))).first()
    if entradas and saidas:
        caixa = entradas - saidas
        return (entradas, saidas, caixa)
    return (0, 0, 0)
