import fastapi
from sqlmodel import Session

from src import auth
from src.db import DBSESSAO_DEP
from src.domain import repository
from src.templates import render

router = fastapi.APIRouter(prefix='', dependencies=[auth.HEADER_AUTH])


@router.get('/home', include_in_schema=False, dependencies=[auth.HEADER_AUTH])
async def get_home(request: fastapi.Request, session: Session = DBSESSAO_DEP):
    db_receitas = repository.count_all(session, repository.Entities.RECEITA)
    db_ingredientes = repository.count_all(session, repository.Entities.INGREDIENTE)
    db_estoques = repository.count_all(session, repository.Entities.ESTOQUE)
    db_vendas = repository.count_all(session, repository.Entities.VENDA)

    db_ultima_venda = repository.get(session, repository.Entities.VENDA, order_by='data_criacao', desc=True, first=True)
    pix_qr_code = None
    pix_mensagem = 'Sem vendas para gerar QR Code.'
    pix_venda = None
    if db_ultima_venda:
        pix_venda = db_ultima_venda
        if db_ultima_venda.recebido:
            pix_qr_code = None
            pix_mensagem = 'A última venda está marcada como <kbd>Recebida</kbd>. Acesse a tela de <a href="/vendas">Vendas</a> para gerar novamente o QR Code caso necessário.'
        else:
            pix_qr_code = repository.get_venda_qr_code(session, db_ultima_venda.id)
            pix_mensagem = f'Use este QR Code para cobrar R$ {db_ultima_venda.valor} referente a <b>{db_ultima_venda.descricao}</b>.'

    return render(request, 'home.html', session, context={
        'len_receitas': db_receitas,
        'len_ingredientes': db_ingredientes,
        'estoques': db_estoques,
        'vendas': db_vendas,
        'pix_qr_code': pix_qr_code,
        'pix_mensagem': pix_mensagem,
        'pix_venda': pix_venda
    })


@router.get('/sobre', include_in_schema=False, dependencies=[auth.HEADER_AUTH])
async def get_sobre(request: fastapi.Request, session: Session = DBSESSAO_DEP):
    return render(request, 'sobre.html', session)
