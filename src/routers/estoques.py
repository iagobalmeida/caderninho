import fastapi
from sqlmodel import Session

from db import SESSION_DEP
from domain import inputs, repository
from templates import render
from templates.context import Button, Context
from utils import redirect_back, redirect_url_for

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
                 'data-bs-target': '#modalCreateEstoque'
             }
        )
    ]
)


@router.get('/', include_in_schema=False)
async def get_estoques_index(request: fastapi.Request, filter_ingrediente_id: int = -1, filter_data_inicio: str = None, filter_data_final: str = None, session: Session = SESSION_DEP):
    db_estoques = repository.list_estoques(session, filter_ingrediente_id, filter_data_inicio, filter_data_final)
    db_ingredientes = repository.get_ingredientes(session)
    entradas, saidas, caixa = repository.get_fluxo_caixa(session)
    return render(
        session=session,
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


@router.post('/', include_in_schema=False)
async def post_estoques_index(request: fastapi.Request, payload: inputs.EstoqueCriar = fastapi.Form(), session: Session = SESSION_DEP):
    repository.create_estoque(
        session,
        descricao=payload.descricao,
        ingrediente_id=payload.ingrediente_id,
        quantidade=payload.quantidade,
        valor_pago=payload.valor_pago
    )
    return redirect_back(request)


@router.post('/excluir', include_in_schema=False)
async def post_estoques_excluir(request: fastapi.Request, id: int = fastapi.Form(), session: Session = SESSION_DEP):
    repository.delete_estoque(session, id=id)
    return redirect_back(request)


@router.post('/atualizar', include_in_schema=False)
async def post_estoques_atualizar(request: fastapi.Request, payload: inputs.EstoqueAtualizar = fastapi.Form(), session: Session = SESSION_DEP):
    repository.update_estoque(session, id=id, nome=payload.nome, peso=payload.peso, custo=payload.custo)
    return redirect_back(request)
