from datetime import datetime, timedelta
from enum import Enum
from math import ceil

from aiocache import Cache
from loguru import logger
from sqlalchemy import func
from sqlmodel import Float, and_, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from caderninho.src.domain.entities import (
    CaixaMovimentacao,
    CaixMovimentacaoTipo,
    Estoque,
    GastoRecorrencia,
    GastoRecorrente,
    GastoTipo,
    Insumo,
    Organizacao,
    Receita,
    ReceitaGasto,
    Usuario,
)
from caderninho.src.schemas.auth import AuthSession


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
CACHE_TTL = 1 * 60 * 20


async def set_cache(*args, value, duration: int = CACHE_TTL):
    key = "_".join([str(a) for a in args])
    __cache = {
        "created_at": datetime.now(),
        "expiration": datetime.now() + timedelta(seconds=duration),
        "value": value,
    }
    await cache.set(key, __cache, duration)
    return __cache


async def get_cache(*args):
    key = "_".join([str(a) for a in args])
    return await cache.get(key)


async def unset_cache(*args):
    key = "_".join([str(a) for a in args])
    return await cache.delete(key)


async def count_all(
    db_session: AsyncSession, entity: Entities, auth_session: AuthSession = None
):
    count_query = select(func.count()).select_from(entity.value)
    if auth_session and not auth_session.administrador:
        count_query = count_query.filter(
            entity.value.organizacao_id == auth_session.organizacao_id
        )
    return (await db_session.exec(count_query)).one()


async def get(
    db_session: AsyncSession,
    entity: Entities,
    filters: dict = {},
    first: bool = False,
    order_by: str = None,
    desc: bool = False,
    per_page: int = 30,
    page: int = 1,
    auth_session: AuthSession = None,
    ignore_validations: bool = False,
):
    query = select(entity.value)

    if filters:
        for key, value in filters.items():
            if value == None:
                continue
            if key == "data_inicio":
                query = query.filter(entity.value.data_criacao >= value)
            elif key == "data_final":
                query = query.filter(entity.value.data_criacao <= value)
            elif key.endswith("__like"):
                key = key.replace("__like", "")
                query = query.filter(getattr(entity.value, key).contains(value))
            else:
                query = query.filter(getattr(entity.value, key) == value)

    if auth_session and not ignore_validations:
        if not auth_session.administrador and entity != Entities.ORGANIZACAO:
            query = query.filter(
                entity.value.organizacao_id == auth_session.organizacao_id
            )

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


async def update(
    db_session: AsyncSession,
    entity: Entities,
    filters: dict = {},
    values: dict = {},
    auth_session: AuthSession = None,
):
    db_entity, _, _ = await get(
        auth_session=auth_session,
        db_session=db_session,
        entity=entity,
        filters=filters,
        first=True,
    )
    if not db_entity:
        raise ValueError(f"{entity} não encontrado!")

    if entity == Entities.USUARIO and "senha_atual" in values:
        if not db_entity.verificar_senha(values["senha_atual"]):
            raise ValueError("Senha atual inválida!")
        del values["senha_atual"]

    if auth_session:
        if not auth_session.administrador and not auth_session.dono:
            if entity == Entities.USUARIO and db_entity.id != auth_session.id:
                raise ValueError("Sem permissão para alterar os dados do usuário!")

            if entity == Entities.ORGANIZACAO:
                raise ValueError(
                    "Sem permissão para alterar as informações da organização!"
                )

    for key, value in [(key, value) for key, value in values.items() if value != None]:
        db_entity.__setattr__(key, value)

    if entity == Entities.USUARIO:
        db_entity.hash_senha()

    await db_session.commit()
    return db_entity


async def delete(
    db_session: AsyncSession,
    entity: Entities,
    filters: dict = {},
    auth_session: AuthSession = None,
):
    if entity == Entities.ORGANIZACAO:
        raise ValueError("Não é possível excluir uma organização!")

    db_entities, _, _ = await get(
        auth_session=auth_session, db_session=db_session, entity=entity, filters=filters
    )

    if not db_entities:
        raise ValueError(f"{entity} não encontrado!")

    for db_entity in db_entities:
        if auth_session:
            if not auth_session.administrador and not auth_session.dono:
                if entity == Entities.USUARIO and db_entity.id != auth_session.id:
                    raise ValueError("Sem permissão para excluir o usuário!")
        await db_session.delete(db_entity)

    await db_session.commit()
    return True


async def create(
    db_session: AsyncSession,
    entity: Entities,
    values: dict = {},
    auth_session: AuthSession = None,
):
    db_entity = entity.value(**values)
    if auth_session:
        if not "organizacao_id" in values and not entity == Entities.ORGANIZACAO:
            if auth_session.administrador:
                raise ValueError(
                    "Administrador não pode criar registros pois não faz parte uma organização"
                )
            db_entity.organizacao_id = auth_session.organizacao_id

    if entity == Entities.USUARIO:
        db_entity.hash_senha()
        logger.info(db_entity)

    db_session.add(db_entity)
    await db_session.commit()
    logger.info(f"Entidade {entity.value.__name__} #{db_entity.id} criada")
    return db_entity


async def bulk_create(
    db_session: AsyncSession,
    entity: Entities,
    values: list = [],
    auth_session: AuthSession = None,
):
    db_entities = []
    for value in values:
        if not isinstance(value, entity.value):
            value = entity.value(**value)
        db_entities.append(value)

    if auth_session:
        if not "organizacao_id" in values and not entity == Entities.ORGANIZACAO:
            if auth_session.administrador:
                raise ValueError(
                    "Administrador não pode criar registros pois não faz parte uma organização"
                )
            for entity in db_entities:
                entity.organizacao_id = auth_session.organizacao_id

    if entity == Entities.USUARIO:
        for entity in db_entities:
            entity.hash_senha()

    db_session.add_all(db_entities)
    await db_session.commit()
    return db_entities


# Funções otimizadas


async def get_caixa_movimentacoes_qr_code(
    auth_session: AuthSession, db_session: AsyncSession, venda_id: str
) -> str:
    organizacao, _, _ = await get(
        auth_session=auth_session,
        db_session=db_session,
        entity=Entities.ORGANIZACAO,
        filters={"id": auth_session.organizacao_id},
        first=True,
    )
    venda, _, _ = await get(
        auth_session=auth_session,
        db_session=db_session,
        entity=Entities.CAIXA_MOVIMENTACAO,
        filters={"id": venda_id},
        first=True,
    )
    return venda.gerar_qr_code(
        pix_nome=organizacao.descricao,
        pix_cidade=organizacao.cidade,
        pix_chave=organizacao.chave_pix,
    )


async def recarregar_cache(auth_session: AuthSession, db_session: AsyncSession):
    return await unset_cache(
        "get_chart_fluxo_caixa_datasets", auth_session.id, auth_session.organizacao_id
    )


async def get_chart_fluxo_caixa_datasets(
    auth_session: AuthSession,
    db_session: AsyncSession,
    data_inicial: datetime,
    data_final: datetime,
) -> dict:
    cached = await get_cache(
        "get_chart_fluxo_caixa_datasets", auth_session.id, auth_session.organizacao_id
    )
    if not cached:
        logger.debug("✖ Cache not found!")
        result = await __get_chart_fluxo_caixa_datasets(
            auth_session=auth_session,
            db_session=db_session,
            data_inicial=data_inicial,
            data_final=data_final,
        )
        return await set_cache(
            "get_chart_fluxo_caixa_datasets",
            auth_session.id,
            auth_session.organizacao_id,
            value=result,
        )
    logger.debug("✔ Cache found")
    return cached


async def __get_chart_fluxo_caixa_datasets(
    auth_session: AuthSession,
    db_session: AsyncSession,
    data_inicial: datetime,
    data_final: datetime,
) -> list:

    # 1. Gerar o esqueleto de datas (Range de datas)
    num_days = (data_final - data_inicial).days + 1
    dates = [(data_inicial + timedelta(days=i)).date() for i in range(num_days)]

    # Dicionário para busca rápida: { date: [data_str, entradas, saidas, margem, recorrentes] }
    res_dict = {d: [d.strftime("%Y-%m-%d"), 0.0, 0.0, 0.0, 0.0] for d in dates}

    # 2. Query de CaixaMovimentacao (SQLModel Style)
    stmt_caixa = (
        select(
            func.date(CaixaMovimentacao.data_criacao).label("dia"),
            func.sum(
                func.cast(CaixaMovimentacao.tipo == CaixMovimentacaoTipo.ENTRADA, Float)
                * CaixaMovimentacao.valor
            ).label("entradas"),
            func.sum(
                func.cast(CaixaMovimentacao.tipo == CaixMovimentacaoTipo.SAIDA, Float)
                * CaixaMovimentacao.valor
            ).label("saidas"),
        )
        .where(
            and_(
                CaixaMovimentacao.organizacao_id == auth_session.organizacao_id,
                CaixaMovimentacao.data_criacao >= data_inicial,
                CaixaMovimentacao.data_criacao <= data_final,
            )
        )
        .group_by(func.date(CaixaMovimentacao.data_criacao))
    )

    caixa_rows = (await db_session.exec(stmt_caixa)).all()
    for dia, entradas, saidas in caixa_rows:
        dia_date = datetime.date(datetime.strptime(dia, "%Y-%m-%d"))
        if dia_date in res_dict:
            res_dict[dia_date][1] += entradas or 0
            res_dict[dia_date][2] += saidas or 0
            res_dict[dia_date][3] += (entradas or 0) - (saidas or 0)

    # 3. Query de Estoque
    stmt_estoque = (
        select(
            func.date(Estoque.data_criacao).label("dia"),
            func.sum(Estoque.valor_pago).label("saidas"),
        )
        .where(
            and_(
                Estoque.organizacao_id == auth_session.organizacao_id,
                Estoque.data_criacao >= data_inicial,
                Estoque.data_criacao <= data_final,
            )
        )
        .group_by(func.date(Estoque.data_criacao))
    )

    estoque_rows = (await db_session.exec(stmt_estoque)).all()
    for dia, saidas in estoque_rows:
        dia_date = datetime.date(datetime.strptime(dia, "%Y-%m-%d"))
        if dia_date in res_dict:
            res_dict[dia_date][2] += saidas or 0
            res_dict[dia_date][3] -= saidas or 0

    # 4. Gasto Recorrente (Simplificado)
    # Aqui mantemos a lógica de negócio, mas usamos Select estruturado
    stmt_recorrente = select(GastoRecorrente).where(
        GastoRecorrente.organizacao_id == auth_session.organizacao_id,
        GastoRecorrente.data_inicio <= data_final,
    )
    recorrentes = (await db_session.exec(stmt_recorrente)).all()
    # ... continuação da função anterior

    for gasto in recorrentes:
        # 1. Ajuste do saldo inicial (Cobranças retroativas até o início da visualização)
        # Se o gasto começou antes da data_inicial, subtraímos o acumulado do "passado" no primeiro dia do gráfico
        if gasto.data_inicio < data_inicial:
            if gasto.recorrencia == GastoRecorrencia.MENSAL:
                meses_passados = (data_inicial - gasto.data_inicio).days // 30
                res_dict[data_inicial.date()][3] -= meses_passados * gasto.valor
            elif gasto.recorrencia == GastoRecorrencia.SEMANAL:
                semanas_passadas = (data_inicial - gasto.data_inicio).days // 7
                res_dict[data_inicial.date()][3] -= semanas_passadas * gasto.valor

        # 2. Distribuição das cobranças dentro do período visível (O loop dos dias)
        for dia_grafico, valores in res_dict.items():
            # Só cobramos se o dia do gráfico for igual ou posterior ao início do gasto
            if dia_grafico < gasto.data_inicio.date():
                continue

            deve_cobrar = False

            # Lógica Mensal: Se o dia do mês coincide
            if gasto.recorrencia == GastoRecorrencia.MENSAL:
                if dia_grafico.day == gasto.data_inicio.day:
                    deve_cobrar = True

            # Lógica Semanal: Se o dia da semana coincide (0=Segunda, 6=Domingo)
            elif gasto.recorrencia == GastoRecorrencia.SEMANAL:
                if dia_grafico.weekday() == gasto.data_inicio.weekday():
                    deve_cobrar = True

            if deve_cobrar:
                valor_final = 0.0
                if gasto.tipo == GastoTipo.FIXO:
                    valor_final = gasto.valor
                else:
                    # Se for percentual, calcula sobre a margem atual (coluna 3)
                    # abs() usado conforme sua lógica original
                    valor_final = abs(valores[3] * gasto.valor / 100)

                valores[3] -= valor_final  # Atualiza Margem
                valores[4] += valor_final  # Acumula em "Recorrentes" (coluna 4)

    return list(res_dict.values())
