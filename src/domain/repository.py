from enum import Enum
from math import ceil
from typing import Tuple

from sqlmodel import func, select

from src.domain.entities import (Estoque, Ingrediente, Organizacao, Receita,
                                 ReceitaIngredienteLink, Usuario, Venda)
from src.schemas.auth import DBSessaoAutenticada


class Entities(Enum):
    ORGANIZACAO = Organizacao
    USUARIO = Usuario
    RECEITA_INGREDIENTE = ReceitaIngredienteLink
    ESTOQUE = Estoque
    VENDA = Venda
    INGREDIENTE = Ingrediente
    RECEITA = Receita


def count_all(session: DBSessaoAutenticada, entity: Entities):
    count_query = select(func.count()).select_from(entity.value)
    return session.exec(count_query).one()


def get(
        session: DBSessaoAutenticada,
        entity: Entities,
        filters: dict = {},
        first: bool = False,
        order_by: str = None,
        desc: bool = False,
        per_page: int = 10,
        page: int = 1,
        ignore_validations: bool = False
):
    query = select(entity.value)

    if filters:
        for key, value in filters.items():
            if value == None:
                continue
            if key == 'data_inicio':
                query = query.filter(entity.value.data_criacao >= value)
            elif key == 'data_final':
                query = query.filter(entity.value.data_criacao <= value)
            else:
                query = query.filter(entity.value.__dict__[key] == value)

    if getattr(session, 'sessao_autenticada', False) and not ignore_validations:
        if not session.sessao_autenticada.administrador and entity != Entities.ORGANIZACAO:
            query = query.filter(getattr(entity, 'organizacao_id') == session.sessao_autenticada.organizacao_id)

    if order_by:
        if desc:
            query = query.order_by(entity.value.__dict__[order_by].desc())
        else:
            query = query.order_by(entity.value.__dict__[order_by])

    if first:
        return session.exec(query).first(), None, None

    count_query = select(func.count()).select_from(query.subquery())
    count = session.exec(count_query).one()

    pages = ceil(count / per_page) if per_page else 1

    query_limit = per_page
    query_offset = per_page * (page - 1)
    query = query.limit(query_limit).offset(query_offset)

    return session.exec(query).all(), pages, count


def update(session: DBSessaoAutenticada, entity: Entities, filters: dict = {}, values: dict = {}):
    db_entity, _, _ = get(session, entity, filters, first=True)

    if not db_entity:
        raise ValueError(f'{entity} não encontrado!')

    if entity == Entities.USUARIO and 'senha_atual' in values:
        if db_entity.senha != values['senha_atual']:
            raise ValueError('Senha atual inválida!')

    if not session.sessao_autenticada.administrador and not session.sessao_autenticada.dono:

        if entity == Entities.USUARIO and db_entity.id != session.sessao_autenticada.id:
            raise ValueError('Sem permissão para alterar os dados do usuário!')

        if entity == Entities.ORGANIZACAO:
            raise ValueError('Sem permissão para alterar as informações da organização!')

    for key, value in values.items():
        if value == None:
            continue
        db_entity.__setattr__(key, value)

    session.commit()
    return db_entity


def delete(session: DBSessaoAutenticada, entity: Entities, filters: dict = {}):
    if entity == Entities.ORGANIZACAO:
        raise ValueError('Não é possível excluir uma organização!')

    db_entities, _, _ = get(session, entity, filters)

    if not db_entities:
        raise ValueError(f'{entity} não encontrado!')

    for db_entity in db_entities:
        if not session.sessao_autenticada.administrador and not session.sessao_autenticada.dono:
            if entity == Entities.USUARIO and db_entity.id != session.sessao_autenticada.id:
                raise ValueError('Sem permissão para excluir o usuário!')
        session.delete(db_entity)

    session.commit()
    return True


def create(session: DBSessaoAutenticada, entity: Entities, values: dict = {}):
    db_entity = entity.value(**values)
    if not 'organizacao_id' in values and not entity == Entities.ORGANIZACAO:
        db_entity.organizacao_id = session.sessao_autenticada.organizacao_id
    session.add(db_entity)
    session.commit()
    return db_entity


# Funções otimizadas

def get_venda_qr_code(session: DBSessaoAutenticada, venda_id: int) -> str:
    organizacao, _, _ = get(session, Entities.ORGANIZACAO, {'id': session.sessao_autenticada.organizacao_id}, first=True)
    if not organizacao:
        return None
    venda, _, _ = get(session, Entities.VENDA, {'id': venda_id}, first=True)
    return venda.gerar_qr_code(
        pix_nome=organizacao.descricao,
        pix_cidade=organizacao.cidade,
        pix_chave=organizacao.chave_pix
    )


def get_fluxo_caixa(session: DBSessaoAutenticada) -> Tuple[float, float, float]:
    query_entradas = select(func.sum(Venda.valor))
    if not session.sessao_autenticada.administrador:
        query_entradas = query_entradas.filter(Venda.organizacao_id == session.sessao_autenticada.organizacao_id)
    entradas = session.exec(query_entradas).first()

    query_saidas = select(func.sum(Estoque.valor_pago))
    if not session.sessao_autenticada.administrador:
        query_saidas = query_saidas.filter(Estoque.organizacao_id == session.sessao_autenticada.organizacao_id)
    saidas = session.exec(query_saidas).first()

    if not entradas and entradas != 0:
        entradas = 0

    if not saidas and saidas != 0:
        saidas = 0

    caixa = entradas - saidas
    return (entradas, saidas, caixa)
