from datetime import datetime, timedelta
from enum import Enum
from math import ceil

from aiocache import Cache
from loguru import logger
from sqlmodel import func, select, text
from sqlmodel.ext.asyncio.session import AsyncSession

from src.domain.entities import (CaixaMovimentacao, Estoque, GastoRecorrencia,
                                 GastoRecorrente, Insumo, Organizacao, Receita,
                                 ReceitaGasto, Usuario)
from src.schemas.auth import AuthSession


class Entities(Enum):
    ORGANIZACAO = Organizacao
    GASTO_RECORRENTE = GastoRecorrente
    USUARIO = Usuario
    RECEITA_GASTO = ReceitaGasto
    ESTOQUE = Estoque
    CAIXA_MOVIMENTACAO = CaixaMovimentacao
    INSUMO = Insumo
    RECEITA = Receita


cache = Cache(Cache.MEMORY)
CACHE_TTL = 1*60*20


async def set_cache(*args, value, duration: int = CACHE_TTL):
    key = '_'.join([str(a) for a in args])
    __cache = {
        'created_at': datetime.now(),
        'expiration': datetime.now() + timedelta(seconds=duration),
        'value': value
    }
    await cache.set(key, __cache, duration)
    return __cache


async def get_cache(*args):
    key = '_'.join([str(a) for a in args])
    return await cache.get(key)


async def unset_cache(*args):
    key = '_'.join([str(a) for a in args])
    return await cache.delete(key)


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

async def get_caixa_movimentacoes_qr_code(auth_session: AuthSession, db_session: AsyncSession, venda_id: int) -> str:
    organizacao, _, _ = await get(auth_session=auth_session, db_session=db_session, entity=Entities.ORGANIZACAO, filters={'id': auth_session.organizacao_id}, first=True)
    if not organizacao:  # pragma: nocover
        return None
    venda, _, _ = await get(auth_session=auth_session, db_session=db_session, entity=Entities.CAIXA_MOVIMENTACAO, filters={'id': venda_id}, first=True)
    return venda.gerar_qr_code(
        pix_nome=organizacao.descricao,
        pix_cidade=organizacao.cidade,
        pix_chave=organizacao.chave_pix
    )


async def recarregar_cache(auth_session: AuthSession, db_session: AsyncSession):
    return await unset_cache('get_chart_fluxo_caixa_datasets', auth_session.id, auth_session.organizacao_id)


async def get_chart_fluxo_caixa_datasets(auth_session: AuthSession, db_session: AsyncSession, data_inicial: datetime, data_final: datetime) -> dict:
    cached = await get_cache('get_chart_fluxo_caixa_datasets', auth_session.id, auth_session.organizacao_id)
    if not cached:
        logger.info('✖ Cache not found!')
        result = await __get_chart_fluxo_caixa_datasets(auth_session=auth_session, db_session=db_session, data_inicial=data_inicial, data_final=data_final)
        return await set_cache('get_chart_fluxo_caixa_datasets', auth_session.id, auth_session.organizacao_id, value=result)
    logger.info('✔ Cache found')
    return cached


async def __get_chart_fluxo_caixa_datasets(auth_session: AuthSession, db_session: AsyncSession, data_inicial: datetime, data_final: datetime) -> dict:
    dates = [(data_inicial + timedelta(days=i)).strftime('%Y-%m-%d') for i in range((data_final - data_inicial).days + 1)]
    results = [
        [data, 0, 0, 0, 0] for data in dates
    ]

    filter_organizacao_id = f'organizacao_id = {auth_session.organizacao_id} AND '
    query_caixa_movimentacao = text(f'''
        SELECT
            date(data_criacao) AS dia,
            sum(CASE WHEN (tipo = 'ENTRADA') THEN valor ELSE 0 END) AS entradas,
            sum(CASE WHEN (tipo = 'SAIDA') THEN valor ELSE 0 END) AS saidas,
            sum(CASE WHEN (tipo = 'ENTRADA') THEN valor ELSE 0 END) - sum(CASE WHEN (tipo = 'SAIDA') THEN valor ELSE 0 END) AS margem
        FROM caixamovimentacao
        WHERE
            {filter_organizacao_id if auth_session.organizacao_id else ''}
            data_criacao >= '{data_inicial.strftime('%Y-%m-%d')}'
            AND data_criacao <= '{data_final.strftime('%Y-%m-%d')}'
        GROUP BY date(data_criacao)
        ORDER BY dia ASC

    ''')
    result_caixa_movimentacao = (await db_session.exec(query_caixa_movimentacao)).all()
    for __row in result_caixa_movimentacao:
        __row_date = str(__row[0])
        try:
            __row_index = dates.index(__row_date)
            for __col in range(len(__row) - 1):
                results[__row_index][__col+1] += __row[__col+1]
        except ValueError:
            results[__row_date] = [
                __row_date,
                __row[1],
                __row[2],
                __row[3],
                0
            ]

    filter_organizacao_id = f'organizacao_id = {auth_session.organizacao_id} AND '
    query_estoque = text(f'''
        SELECT
            date(data_criacao) AS dia,
            sum(0) AS entradas,
            sum(valor_pago) AS saidas,
            -1 * sum(valor_pago) AS margem
        FROM estoque
        WHERE
            {filter_organizacao_id if auth_session.organizacao_id else ''}
            data_criacao >= '{data_inicial.strftime('%Y-%m-%d')}'
            AND data_criacao <= '{data_final.strftime('%Y-%m-%d')}'
        GROUP BY date(data_criacao)
        ORDER BY dia ASC
    ''')
    result_estoque = (await db_session.exec(query_estoque)).all()
    for __row in result_estoque:
        __row_date = str(__row[0])
        try:
            __row_index = dates.index(__row[0])
            for __col in range(len(__row) - 1):
                results[__row_index][__col+1] += __row[__col+1]
        except ValueError:
            results[__row_date] = [
                __row_date,
                __row[1],
                __row[2],
                __row[3],
                0
            ]

    filter_organizacao_id = f'organizacao_id = {auth_session.organizacao_id} AND '
    query_recorrentes = text(f'''
        SELECT
            date(data_inicio) AS dia,
            recorrencia AS recorrencia,
            tipo AS tipo,
            valor AS valor
        FROM gastorecorrente
        WHERE
            {filter_organizacao_id if auth_session.organizacao_id else ''}
            data_inicio <= '{data_final.strftime('%Y-%m-%d')}'
    ''')
    result_recorrentes = (await db_session.exec(query_recorrentes)).all()

    for __row in result_recorrentes:
        __row_date = datetime.strptime(str(__row[0]), '%Y-%m-%d')

        if str(__row[1]).title() == GastoRecorrencia.MENSAL.value:
            cobrancas_anteriores = int((datetime.now() - __row_date).days/30)
            results[0][3] -= cobrancas_anteriores * __row[3]

            dia_cobranca = __row_date.day
            for r in results:
                if int(r[0].split('-')[-1]) == int(dia_cobranca):
                    if __row[2] == 'FIXO':
                        r[3] -= __row[3]
                        r[4] += __row[3]
                    else:
                        __value = abs(r[3] * __row[3]/100)
                        r[3] -= __value
                        r[4] += __value
        elif str(__row[1]).title() == GastoRecorrencia.SEMANAL.value:
            dia_cobranca = __row_date.weekday()

            cobrancas_anteriores = int((datetime.now() - __row_date).days/7)
            results[0][3] -= cobrancas_anteriores * __row[3]

            for r in results:
                if datetime.strptime(r[0], '%Y-%m-%d').weekday() == dia_cobranca:
                    if __row[2] == 'FIXO':
                        r[3] -= __row[3]
                        r[4] += __row[3]
                    else:
                        __value = abs(r[3] * __row[3]/100)
                        r[3] -= __value
                        r[4] += __value
                        logger.info(r[4])

    return results
