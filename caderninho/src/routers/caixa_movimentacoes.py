from uuid import UUID

import fastapi
from sqlmodel import Session

from caderninho.src import auth
from caderninho.src.db import DBSESSAO_DEP
from caderninho.src.domain import inputs, repository
from caderninho.src.services import delete_entity, list_entity
from caderninho.src.utils import redirect_back

router = fastapi.APIRouter(
    prefix="/app/caixa_movimentacoes", dependencies=[auth.HEADER_AUTH]
)


@router.get("/", include_in_schema=False)
async def get_caixa_movimentacoes_index(
    request: fastapi.Request,
    page: int = fastapi.Query(1),
    db_session: Session = DBSESSAO_DEP,
):
    return await list_entity(
        request=request,
        db_session=db_session,
        entity=repository.Entities.CAIXA_MOVIMENTACAO,
        page=page,
        filters={},
    )


@router.post("/", include_in_schema=False)
async def post_caixa_movimentacoes_index(
    request: fastapi.Request,
    payload: inputs.CaixaMovimentacaoCriar = fastapi.Form(),
    session: Session = DBSESSAO_DEP,
):
    auth_session = getattr(request.state, "auth", None)
    await repository.create(
        auth_session=auth_session,
        db_session=session,
        entity=repository.Entities.CAIXA_MOVIMENTACAO,
        values={
            "descricao": payload.descricao,
            "tipo": payload.tipo,
            "valor": payload.valor,
        },
    )
    return redirect_back(request, message="Movimentação de caixa criada com sucesso!")


@router.post("/excluir", include_in_schema=False)
async def post_caixa_movimentacao_excluir(
    request: fastapi.Request,
    selecionados_ids: str = fastapi.Form(),
    db_session: Session = DBSESSAO_DEP,
):
    return await delete_entity(
        request=request,
        db_session=db_session,
        entity=repository.Entities.CAIXA_MOVIMENTACAO,
        ids=selecionados_ids.split(","),
    )


@router.post("/marcar/recebido", include_in_schema=False)
async def post_caixa_movimentacoes_marcar_recebido(
    request: fastapi.Request,
    selecionados_ids: str = fastapi.Form(),
    session: Session = DBSESSAO_DEP,
):
    auth_session = getattr(request.state, "auth", None)
    if selecionados_ids:
        for id in selecionados_ids.split(","):
            await repository.update(
                auth_session=auth_session,
                db_session=session,
                entity=repository.Entities.CAIXA_MOVIMENTACAO,
                filters={"id": UUID(id)},
                values={"recebido": True},
            )
    return redirect_back(
        request, message="CaixaMovimentacao(s) atualizada(s) com sucesso!"
    )


@router.post("/marcar/pendente", include_in_schema=False)
async def post_caixa_movimentacoes_marcar_pendente(
    request: fastapi.Request,
    selecionados_ids: str = fastapi.Form(),
    session: Session = DBSESSAO_DEP,
):
    auth_session = getattr(request.state, "auth", None)
    if selecionados_ids:
        for id in selecionados_ids.split(","):
            await repository.update(
                auth_session=auth_session,
                db_session=session,
                entity=repository.Entities.CAIXA_MOVIMENTACAO,
                filters={"id": UUID(id)},
                values={"recebido": False},
            )
    return redirect_back(
        request, message="CaixaMovimentacao(s) atualizada(s) com sucesso!"
    )


@router.post("/atualizar", include_in_schema=False)
async def post_caixa_movimentacoes_atualizar(
    request: fastapi.Request,
    payload: inputs.CaixaMovimentacaoAtualizar = fastapi.Form(),
    session: Session = DBSESSAO_DEP,
):
    auth_session = getattr(request.state, "auth", None)
    await repository.update(
        auth_session=auth_session,
        db_session=session,
        entity=repository.Entities.CAIXA_MOVIMENTACAO,
        filters={"id": payload.id},
        values={
            "descricao": payload.descricao,
            "valor": payload.valor,
            "recebido": True if payload.recebido else False,
        },
    )
    return redirect_back(request, message="CaixaMovimentacao atualizada com sucesso!")
