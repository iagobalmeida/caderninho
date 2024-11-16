import fastapi
from sqlmodel import Session

from src.db import SESSION_DEP
from src.decorators.auth import authorized
from src.domain import inputs, repository
from src.templates import render
from src.templates.context import Button, Context
from src.utils import redirect_back

router = fastapi.APIRouter(prefix='/vendas')
context_header = Context.Header(
    pretitle='Registros',
    title='Vendas',
    symbol='shopping_cart',
    buttons=[
        Button(
            content='Apagar Selecionados',
            classname='btn',
            symbol='delete',
            attributes={
                'disabled': 'true',
                'data-bs-toggle': 'modal',
                'data-bs-target': '#modalDeleteVenda',
                'id': 'btn-apagar-selecionados'
            }
        ),
        Button(
            content='Criar Venda',
            classname='btn btn-success',
            symbol='add',
            attributes={
                'data-bs-toggle': 'modal',
                'data-bs-target': '#modalCreateVenda'
            }
        )
    ]
)


@router.get('/', include_in_schema=False)
@authorized
async def get_vendas_index(request: fastapi.Request, filter_data_inicio: str = None, filter_data_final: str = None, session: Session = SESSION_DEP):
    db_vendas = repository.list_vendas(session, filter_data_inicio, filter_data_final)
    entradas, saidas, caixa = repository.get_fluxo_caixa(session)
    return render(
        session=session,
        request=request,
        template_name='vendas/list.html',
        context={
            'header': context_header,
            'vendas': db_vendas,
            'entradas': entradas,
            'saidas': saidas,
            'caixa': caixa,
            'filter_data_inicio': filter_data_inicio,
            'filter_data_final': filter_data_final
        }
    )


@router.post('/', include_in_schema=False)
@authorized
async def post_vendas_index(request: fastapi.Request, payload: inputs.VendaCriar = fastapi.Form(), session: Session = SESSION_DEP):
    repository.create_venda(session, descricao=payload.descricao, valor=payload.valor)
    return redirect_back(request)


@router.post('/excluir', include_in_schema=False)
@authorized
async def post_vendas_excluir(request: fastapi.Request, selecionados_ids: str = fastapi.Form(), session: Session = SESSION_DEP):
    if selecionados_ids:
        for id in selecionados_ids.split(','):
            repository.delete_venda(session, id=int(id))
    return redirect_back(request)


@router.post('/atualizar', include_in_schema=False)
@authorized
async def post_vendas_atualizar(request: fastapi.Request, payload: inputs.VendaAtualizar = fastapi.Form(), session: Session = SESSION_DEP):
    repository.update_venda(session, id=payload.id, descricao=payload.descricao, valor=payload.valor)
    return redirect_back(request)
