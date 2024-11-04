import fastapi
from sqlmodel import Session

from db import SESSION_DEP
from domain import repository
from templates import render
from templates.context import Button, Context

router = fastapi.APIRouter(prefix='/estoques')
context_header = Context.Header(
    pretitle='Registros',
    title='Estoque',
    symbol='home_storage',
    buttons=[
        Button(
             content='Nova Movimentação',
             classname='btn btn-success',
             symbol='add',
             attributes={
                 'data-bs-toggle': 'modal',
                 'data-bs-target': '#novoIngredienteModal'
             }
        )
    ]
)


@router.get('/')
async def get_estoques_index(request: fastapi.Request, filter_ingrediente_id: int = -1, filter_data_inicio: str = None, filter_data_final: str = None, session: Session = SESSION_DEP):
    db_estoques = repository.list_estoques(session, filter_ingrediente_id, filter_data_inicio, filter_data_final)
    db_ingredientes = repository.get_ingredientes(session)
    entradas, saidas, caixa = repository.get_fluxo_caixa(session)
    return render(
        request=request,
        template_name='estoques/list.html',
        context={
            'header': context_header,
            'estoques': db_estoques,
            'ingredientes': db_ingredientes,
            'entradas': entradas,
            'saidas': saidas,
            'caixa': caixa,
            'filter_ingrediente_id': filter_ingrediente_id,
            'filter_data_inicio': filter_data_inicio,
            'filter_data_final': filter_data_final
        }
    )
