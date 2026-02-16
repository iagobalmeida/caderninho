from pathlib import Path

import fastapi
from sqlmodel import Session

from caderninho.src import auth
from caderninho.src.db import DBSESSAO_DEP
from caderninho.src.domain import repository
from caderninho.src.domain.schemas import CaixMovimentacaoTipo
from caderninho.src.schemas.docs import SOBRE_ESSA_PAGINA
from caderninho.src.templates import render
from caderninho.src.templates.context import Context

router = fastapi.APIRouter(prefix="/app", dependencies=[auth.HEADER_AUTH])

LOG_FILE = "logs/app.log"


@router.get("/home", include_in_schema=False, dependencies=[auth.HEADER_AUTH])
async def get_home(request: fastapi.Request, session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, "auth", None)
    db_receitas = await repository.count_all(
        auth_session=auth_session,
        db_session=session,
        entity=repository.Entities.RECEITA,
    )
    db_insumos = await repository.count_all(
        auth_session=auth_session, db_session=session, entity=repository.Entities.INSUMO
    )
    db_estoques = await repository.count_all(
        auth_session=auth_session,
        db_session=session,
        entity=repository.Entities.ESTOQUE,
    )
    db_vendas = await repository.count_all(
        auth_session=auth_session,
        db_session=session,
        entity=repository.Entities.CAIXA_MOVIMENTACAO,
    )

    db_ultima_venda, _, _ = await repository.get(
        auth_session=auth_session,
        db_session=session,
        entity=repository.Entities.CAIXA_MOVIMENTACAO,
        order_by="data_criacao",
        filters={"tipo": CaixMovimentacaoTipo.ENTRADA},
        desc=True,
        first=True,
    )
    pix_qr_code = None
    pix_mensagem = "Sem vendas para gerar QR Code."
    pix_venda = None
    if db_ultima_venda:
        pix_venda = db_ultima_venda
        if db_ultima_venda.recebido:
            pix_qr_code = None
            pix_mensagem = 'A última venda está marcada como <kbd>Recebida</kbd>.<br>Acesse a tela de <a href="/vendas">Caixa</a> para gerar novamente o QR Code caso necessário.'
        else:
            pix_qr_code = await repository.get_caixa_movimentacoes_qr_code(
                auth_session=auth_session,
                db_session=session,
                venda_id=db_ultima_venda.id,
            )
            pix_mensagem = f"Use este QR Code para cobrar R$ {db_ultima_venda.valor} referente a <b>{db_ultima_venda.descricao}</b>."

    return await render(
        request,
        "home.html",
        session,
        context={
            "len_receitas": db_receitas,
            "len_insumos": db_insumos,
            "estoques": db_estoques,
            "vendas": db_vendas,
            "pix_qr_code": pix_qr_code,
            "pix_mensagem": pix_mensagem,
            "pix_venda": pix_venda,
        },
    )


# @router.get('/sobre', include_in_schema=False, dependencies=[auth.HEADER_AUTH])
# async def get_sobre(request: fastapi.Request, session: Session = DBSESSAO_DEP):
#     context_header = Context.Header(pretitle='Caderninho', title='Sobre', symbol='info')
#     return await render(request, 'sobre.html', session, context={'header': context_header})


@router.get("/como_usar", include_in_schema=False, dependencies=[auth.HEADER_AUTH])
async def get_como_usar(request: fastapi.Request, session: Session = DBSESSAO_DEP):
    context_header = Context.Header(
        pretitle="Caderninho", title="Documentação Completa", symbol="help"
    )
    return await render(
        request,
        "como_usar.html",
        session,
        {"header": context_header, "sobre_essa_pagina": SOBRE_ESSA_PAGINA},
    )


@router.get("/admin/logs", include_in_schema=False, dependencies=[auth.HEADER_AUTH])
async def get_admin_logs(
    request: fastapi.Request, lines: int = 100, session: Session = DBSESSAO_DEP
):
    auth_session = getattr(request.state, "auth", None)
    if not auth_session.administrador:
        raise ValueError("Sem permissão para acessar esta página")

    log_path = Path(LOG_FILE)

    if not log_path.exists():
        raise ValueError("Arquivo de logs não encontrado")

    with log_path.open("r", encoding="utf-8") as f:
        log_lines = f.readlines()

    lines = min(1000, lines)

    return await render(
        request, "admin/logs.html", session, context={"logs": log_lines[-lines:]}
    )
