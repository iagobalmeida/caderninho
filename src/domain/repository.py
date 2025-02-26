from datetime import datetime, timedelta
from enum import Enum
from math import ceil
from typing import Tuple

from loguru import logger
from sqlalchemy.orm import joinedload
from sqlmodel import Session, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.domain.entities import (Estoque, Insumo, Organizacao, Receita,
                                 ReceitaInsumoLink, Usuario, Venda)
from src.schemas.auth import AuthSession


class Entities(Enum):
    ORGANIZACAO = Organizacao
    USUARIO = Usuario
    RECEITA_INGREDIENTE = ReceitaInsumoLink
    ESTOQUE = Estoque
    VENDA = Venda
    INSUMO = Insumo
    RECEITA = Receita


async def count_all(db_session: AsyncSession, entity: Entities, auth_session: AuthSession = None):
    count_query = select(func.count()).select_from(entity.value)
    if auth_session and not auth_session.administrador:
        count_query = count_query.filter(entity.value.organizacao_id == auth_session.organizacao_id)
    return (await db_session.exec(count_query)).one()


async def get(
        db_session: AsyncSession,
        entity: Entities,
        filters: dict = {},
        first: bool = False,
        order_by: str = None,
        desc: bool = False,
        per_page: int = 10,
        page: int = 1,
        auth_session: AuthSession = None,
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

    if auth_session and not ignore_validations:
        if not auth_session.administrador and entity != Entities.ORGANIZACAO:
            query = query.filter(entity.value.organizacao_id == auth_session.organizacao_id)

    if order_by:
        if desc:
            query = query.order_by(entity.value.__dict__[order_by].desc())
        else:
            query = query.order_by(entity.value.__dict__[order_by])

    if first:
        result = (await db_session.exec(query)).first()
        return result, None, None

    count_query = select(func.count()).select_from(query.subquery())
    count = (await db_session.exec(count_query)).one()

    pages = ceil(count / per_page) if per_page else 1

    query_limit = per_page
    query_offset = per_page * (page - 1)
    query = query.limit(query_limit).offset(query_offset)

    result = (await db_session.exec(query)).all()

    return result, pages, count


async def update(db_session: AsyncSession, entity: Entities, filters: dict = {}, values: dict = {}, auth_session: AuthSession = None):
    db_entity, _, _ = await get(auth_session=auth_session, db_session=db_session, entity=entity, filters=filters, first=True)
    if not db_entity:
        raise ValueError(f'{entity} não encontrado!')

    if entity == Entities.USUARIO and 'senha_atual' in values:
        if not db_entity.verificar_senha(values['senha_atual']):
            raise ValueError('Senha atual inválida!')
        del values['senha_atual']

    if auth_session:
        if not auth_session.administrador and not auth_session.dono:
            if entity == Entities.USUARIO and db_entity.id != auth_session.id:
                raise ValueError('Sem permissão para alterar os dados do usuário!')

            if entity == Entities.ORGANIZACAO:
                raise ValueError('Sem permissão para alterar as informações da organização!')

    for key, value in values.items():
        if value == None:
            continue
        db_entity.__setattr__(key, value)

    if entity == Entities.USUARIO:
        db_entity.hash_senha()

    await db_session.commit()
    return db_entity


async def delete(db_session: AsyncSession, entity: Entities, filters: dict = {}, auth_session: AuthSession = None):
    if entity == Entities.ORGANIZACAO:
        raise ValueError('Não é possível excluir uma organização!')

    db_entities, _, _ = await get(auth_session=auth_session, db_session=db_session, entity=entity, filters=filters)

    if not db_entities:
        raise ValueError(f'{entity} não encontrado!')

    for db_entity in db_entities:
        if auth_session:
            if not auth_session.administrador and not auth_session.dono:
                if entity == Entities.USUARIO and db_entity.id != auth_session.id:
                    raise ValueError('Sem permissão para excluir o usuário!')
        await db_session.delete(db_entity)

    await db_session.commit()
    return True


async def create(db_session: AsyncSession, entity: Entities, values: dict = {}, auth_session: AuthSession = None):
    db_entity = entity.value(**values)
    if auth_session:
        if not 'organizacao_id' in values and not entity == Entities.ORGANIZACAO:
            if auth_session.administrador:
                raise ValueError('Administrador não pode criar registros pois não faz parte uma organização')
            db_entity.organizacao_id = auth_session.organizacao_id

    if entity == Entities.USUARIO:
        db_entity.hash_senha()
        logger.info(db_entity)

    db_session.add(db_entity)
    await db_session.commit()
    logger.info(f'Entidade {entity.value.__name__} #{db_entity.id} criada')
    return db_entity


# Funções otimizadas

async def get_venda_qr_code(auth_session: AuthSession, db_session: AsyncSession, venda_id: int) -> str:
    organizacao, _, _ = await get(auth_session=auth_session, db_session=db_session, entity=Entities.ORGANIZACAO, filters={'id': auth_session.organizacao_id}, first=True)
    if not organizacao:  # pragma: nocover
        return None
    venda, _, _ = await get(auth_session=auth_session, db_session=db_session, entity=Entities.VENDA, filters={'id': venda_id}, first=True)
    return venda.gerar_qr_code(
        pix_nome=organizacao.descricao,
        pix_cidade=organizacao.cidade,
        pix_chave=organizacao.chave_pix
    )


async def get_fluxo_caixa(auth_session: AuthSession, db_session: AsyncSession) -> Tuple[float, float, float]:
    data_limite = datetime.now() - timedelta(days=30)

    query_entradas = select(func.sum(Venda.valor)).where(Venda.data_criacao >= data_limite)
    if getattr(db_session, 'sessao_autenticada', False) and not auth_session.administrador:
        query_entradas = query_entradas.filter(Venda.organizacao_id == auth_session.organizacao_id)
    entradas = (await db_session.exec(query_entradas)).first()

    query_saidas = select(func.sum(Estoque.valor_pago)).where(Venda.data_criacao >= data_limite)
    if getattr(db_session, 'sessao_autenticada', False) and not auth_session.administrador:
        query_saidas = query_saidas.filter(Estoque.organizacao_id == auth_session.organizacao_id)
    saidas = (await db_session.exec(query_saidas)).first()

    caixa = (entradas if entradas else 0) - (saidas if saidas else 0)
    return (entradas, saidas, caixa)
