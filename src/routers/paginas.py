
import fastapi
from sqlmodel import Session

from src import auth
from src.db import SESSION_DEP
from src.domain import repository
from src.templates import render

router = fastapi.APIRouter(prefix='', dependencies=[auth.HEADER_AUTH])


@router.get('/home', include_in_schema=False, dependencies=[auth.HEADER_AUTH])
async def get_home(request: fastapi.Request, session: Session = SESSION_DEP):
    db_receitas = repository.list_receitas(session)
    db_ingredientes = repository.get_ingredientes(session)
    db_estoques = repository.list_estoques(session)
    db_vendas = repository.list_vendas(session)

    return render(request, 'home.html', session, context={
        'len_receitas': len(db_receitas),
        'len_ingredientes': len(db_ingredientes),
        'estoques': len(db_estoques),
        'vendas': len(db_vendas),
    })


@router.get('/sobre', include_in_schema=False, dependencies=[auth.HEADER_AUTH])
async def get_sobre(request: fastapi.Request, session: Session = SESSION_DEP):
    return render(request, 'sobre.html', session)
