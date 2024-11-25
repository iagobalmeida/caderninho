import fastapi
from sqlmodel import Session

from src import auth
from src.db import DBSESSAO_DEP
from src.domain import repository
from src.templates import render

router = fastapi.APIRouter(prefix='', dependencies=[auth.HEADER_AUTH])


@router.get('/home', include_in_schema=False, dependencies=[auth.HEADER_AUTH])
async def get_home(request: fastapi.Request, session: Session = DBSESSAO_DEP):
    db_receitas = repository.get(session, repository.Entities.RECEITA)
    db_ingredientes = repository.get(session, repository.Entities.INGREDIENTE)
    db_estoques = repository.get(session, repository.Entities.ESTOQUE)
    db_vendas = repository.get(session, repository.Entities.VENDA, order_by='data_criacao', desc=True)

    pix_qr_code = None
    pix_mensagem = 'Sem vendas para gerar QR Code.'

    if db_vendas:
        if db_vendas[0].recebido:
            pix_qr_code = None
            pix_mensagem = 'A última venda está marcada como <kbd>Recebida</kbd>. Acesse a tela de vendas para gerar novamente o QR Code caso necessário.'
        else:
            pix_qr_code = repository.get_venda_qr_code(session, db_vendas[0].id)
            pix_mensagem = f'Use este QR Code para cobrar R$ {db_vendas[0].valor} referente a <b>{db_vendas[0].descricao}</b>.'

    return render(request, 'home.html', session, context={
        'len_receitas': len(db_receitas),
        'len_ingredientes': len(db_ingredientes),
        'estoques': len(db_estoques),
        'vendas': len(db_vendas),
        'pix_qr_code': pix_qr_code,
        'pix_mensagem': pix_mensagem
    })


@router.get('/sobre', include_in_schema=False, dependencies=[auth.HEADER_AUTH])
async def get_sobre(request: fastapi.Request, session: Session = DBSESSAO_DEP):
    return render(request, 'sobre.html', session)
