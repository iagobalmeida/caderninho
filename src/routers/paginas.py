import fastapi
from pixqrcode import PixQrCode
from sqlmodel import Session

from src import auth
from src.db import DBSESSAO_DEP
from src.domain import repository
from src.templates import render

router = fastapi.APIRouter(prefix='', dependencies=[auth.HEADER_AUTH])


@router.get('/home', include_in_schema=False, dependencies=[auth.HEADER_AUTH])
async def get_home(request: fastapi.Request, session: Session = DBSESSAO_DEP):
    db_receitas = repository.list_receitas(session)
    db_ingredientes = repository.get_ingredientes(session)
    db_estoques = repository.list_estoques(session)
    db_vendas = repository.list_vendas(session)

    pix_qr_code = None
    if db_vendas:
        pix_qr_code = repository.venda_gerar_qr_code(session, db_vendas[-1].id)

    return render(request, 'home.html', session, context={
        'len_receitas': len(db_receitas),
        'len_ingredientes': len(db_ingredientes),
        'estoques': len(db_estoques),
        'vendas': len(db_vendas),
        'qr_code': pix_qr_code
    })


@router.get('/sobre', include_in_schema=False, dependencies=[auth.HEADER_AUTH])
async def get_sobre(request: fastapi.Request, session: Session = DBSESSAO_DEP):
    return render(request, 'sobre.html', session)
