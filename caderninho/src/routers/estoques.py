from datetime import datetime
from uuid import UUID

import fastapi
from sqlmodel import Session

from caderninho.src import auth
from caderninho.src.db import DBSESSAO_DEP
from caderninho.src.domain import inputs, repository
from caderninho.src.services import delete_entity, list_entity
from caderninho.src.utils import redirect_back

router = fastapi.APIRouter(prefix="/app/estoques", dependencies=[auth.HEADER_AUTH])


@router.get("/", include_in_schema=False)
async def get_estoques_index(
    request: fastapi.Request,
    page: int = fastapi.Query(1),
    per_page: int = fastapi.Query(30),
    filter_insumo_id: UUID = None,
    filter_data_inicio: str = None,
    filter_data_final: str = None,
    db_session: Session = DBSESSAO_DEP,
):
    filters = {}
    if filter_data_inicio:
        filters.update(data_inicio=datetime.strptime(filter_data_inicio, "%Y-%m-%d"))
    if filter_data_final:
        filters.update(data_final=datetime.strptime(filter_data_final, "%Y-%m-%d"))
    if filter_insumo_id != None:
        filters.update(insumo_id=filter_insumo_id)

    return await list_entity(
        request=request,
        db_session=db_session,
        entity=repository.Entities.ESTOQUE,
        page=page,
        per_page=per_page,
        filters=filters,
    )


@router.post("/", include_in_schema=False)
async def post_estoques_index(
    request: fastapi.Request,
    payload: inputs.EstoqueCriar = fastapi.Form(),
    session: Session = DBSESSAO_DEP,
):
    auth_session = getattr(request.state, "auth", None)
    descricao = payload.descricao.lower() if payload.descricao else None
    if descricao == "uso em receita" and payload.receita_id:
        db_receita, _, _ = await repository.get(
            auth_session=auth_session,
            db_session=session,
            entity=repository.Entities.RECEITA,
            filters={"id": UUID(payload.receita_id)},
            first=True,
        )

        descricao = f"Uso em Receita ({db_receita.nome})"

        movimentacoes_criadas = []
        gastos_insumos = [gasto for gasto in db_receita.gastos if gasto.insumo_id]
        for gasto in gastos_insumos:
            quantidade = -1 * gasto.quantidade * float(payload.quantidade_receita)
            movimentacao = await repository.create(
                auth_session=auth_session,
                db_session=session,
                entity=repository.Entities.ESTOQUE,
                values={
                    "descricao": descricao,
                    "insumo_id": gasto.insumo_id,
                    "quantidade": quantidade,
                    "valor_pago": 0,
                },
            )
            movimentacoes_criadas.append(
                (
                    movimentacao.descricao,
                    movimentacao.insumo_id,
                    movimentacao.quantidade,
                )
            )
    else:
        quantidade = (
            float(payload.quantidade_insumo) if payload.quantidade_insumo else None
        )
        if descricao != "compra" and quantidade:
            quantidade = quantidade * -1
        if descricao == "outros" and payload.descricao_customizada:
            descricao = payload.descricao_customizada
        await repository.create(
            auth_session=auth_session,
            db_session=session,
            entity=repository.Entities.ESTOQUE,
            values={
                "descricao": descricao.title(),
                "insumo_id": payload.insumo_id,
                "quantidade": quantidade,
                "valor_pago": float(payload.valor_pago) if payload.valor_pago else 0,
            },
        )
    return redirect_back(request, message="Movimentação criada com sucesso!")


@router.post("/excluir", include_in_schema=False)
async def post_estoque_excluir(
    request: fastapi.Request,
    selecionados_ids: str = fastapi.Form(),
    session: Session = DBSESSAO_DEP,
):
    return await delete_entity(
        request=request,
        db_session=session,
        entity=repository.Entities.ESTOQUE,
        ids=selecionados_ids.split(","),
    )


@router.post("/atualizar", include_in_schema=False)
async def post_estoques_atualizar(
    request: fastapi.Request,
    payload: inputs.EstoqueAtualizar = fastapi.Form(),
    session: Session = DBSESSAO_DEP,
):
    auth_session = getattr(request.state, "auth", None)
    await repository.update(
        auth_session=auth_session,
        db_session=session,
        entity=repository.Entities.ESTOQUE,
        filters={"id": payload.id},
        values={
            "descricao": payload.descricao,
            "valor_pago": payload.valor_pago,
            "quantidade": payload.quantidade,
            "insumo_id": payload.insumo_id,
        },
    )
    return redirect_back(request, message="Movimentação atualizada com sucesso!")
