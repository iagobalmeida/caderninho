from pathlib import Path

import fastapi
from sqlmodel import Session

from src import auth
from src.db import DBSESSAO_DEP
from src.domain import repository
from src.schemas.docs import SOBRE_ESSA_PAGINA
from src.templates import render
from src.templates.context import Context

router = fastapi.APIRouter(prefix='/app', dependencies=[auth.HEADER_AUTH])

LOG_FILE = "logs/app.log"


@router.get('/home', include_in_schema=False, dependencies=[auth.HEADER_AUTH])
async def get_home(request: fastapi.Request, session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    db_receitas = repository.count_all(auth_session=auth_session, db_session=session, entity=repository.Entities.RECEITA)
    db_insumos = repository.count_all(auth_session=auth_session, db_session=session, entity=repository.Entities.INSUMO)
    db_estoques = repository.count_all(auth_session=auth_session, db_session=session, entity=repository.Entities.ESTOQUE)
    db_vendas = repository.count_all(auth_session=auth_session, db_session=session, entity=repository.Entities.VENDA)

    db_ultima_venda, _, _ = repository.get(auth_session=auth_session, db_session=session, entity=repository.Entities.VENDA, order_by='data_criacao', desc=True, first=True)
    pix_qr_code = None
    pix_mensagem = 'Sem vendas para gerar QR Code.'
    pix_venda = None
    if db_ultima_venda:
        pix_venda = db_ultima_venda
        if db_ultima_venda.recebido:
            pix_qr_code = None
            pix_mensagem = 'A última venda está marcada como <kbd>Recebida</kbd>. Acesse a tela de <a href="/vendas">Vendas</a> para gerar novamente o QR Code caso necessário.'
        else:
            pix_qr_code = repository.get_venda_qr_code(auth_session=auth_session, db_session=session, venda_id=db_ultima_venda.id)
            pix_mensagem = f'Use este QR Code para cobrar R$ {db_ultima_venda.valor} referente a <b>{db_ultima_venda.descricao}</b>.'

    return render(request, 'home.html', session, context={
        'len_receitas': db_receitas,
        'len_insumos': db_insumos,
        'estoques': db_estoques,
        'vendas': db_vendas,
        'pix_qr_code': pix_qr_code,
        'pix_mensagem': pix_mensagem,
        'pix_venda': pix_venda
    })


# @router.get('/sobre', include_in_schema=False, dependencies=[auth.HEADER_AUTH])
# async def get_sobre(request: fastapi.Request, session: Session = DBSESSAO_DEP):
#     context_header = Context.Header(pretitle='Caderninho', title='Sobre', symbol='info')
#     return render(request, 'sobre.html', session, context={'header': context_header})


@router.get('/como_usar', include_in_schema=False, dependencies=[auth.HEADER_AUTH])
async def get_como_usar(request: fastapi.Request, session: Session = DBSESSAO_DEP):
    context_header = Context.Header(pretitle='Caderninho', title='Documentação Completa', symbol='help')
    return render(request, 'como_usar.html', session, {
        'header': context_header,
        'sobre_essa_pagina': SOBRE_ESSA_PAGINA
    })


@router.get('/admin/logs', include_in_schema=False, dependencies=[auth.HEADER_AUTH])
async def get_admin_logs(request: fastapi.Request, lines: int = 100, session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    if not auth_session.administrador:
        raise ValueError('Sem permissão para acessar esta página')

    log_path = Path(LOG_FILE)

    if not log_path.exists():
        raise ValueError("Arquivo de logs não encontrado")

    with log_path.open("r", encoding="utf-8") as f:
        log_lines = f.readlines()

    lines = min(1000, lines)

    return render(request, 'admin/logs.html', session, context={
        'logs': log_lines[-lines:]
    })
