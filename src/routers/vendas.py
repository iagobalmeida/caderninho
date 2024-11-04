import fastapi
from sqlmodel import Session

from db import SESSION_DEP
from domain import repository
from templates import render
from templates.context import Button, Context

router = fastapi.APIRouter(prefix='/vendas')
context_header = Context.Header(
    pretitle='Registros',
    title='Vendas',
    symbol='shopping_cart',
    buttons=[
        Button(
            content='Nova Venda',
            classname='btn btn-success',
            symbol='add',
            attributes={
                'data-bs-toggle': 'modal',
                'data-bs-target': '#novaVendaModal'
            }
        )
    ]
)


@router.get('/')
async def get_vendas_index(request: fastapi.Request, session: Session = SESSION_DEP):
    db_vendas = repository.get_vendas(session)
    entradas, saidas, caixa = repository.get_fluxo_caixa(session)
    return render(
        request=request,
        template_name='vendas/list.html',
        context={
            'header': context_header,
            'vendas': db_vendas,
            'entradas': entradas,
            'saidas': saidas,
            'caixa': caixa
        }
    )
