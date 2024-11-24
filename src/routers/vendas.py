import json

import fastapi
from sqlmodel import Session

from src import auth
from src.db import DBSESSAO_DEP
from src.domain import inputs, repository
from src.templates import render
from src.templates.context import Button, Context
from src.utils import redirect_back

router = fastapi.APIRouter(prefix='/vendas', dependencies=[auth.HEADER_AUTH])


@router.get('/', include_in_schema=False)
async def get_vendas_index(request: fastapi.Request, filter_data_inicio: str = None, filter_data_final: str = None, session: Session = DBSESSAO_DEP):
    db_vendas = repository.list_vendas(session, filter_data_inicio, filter_data_final)
    entradas, saidas, caixa = repository.get_fluxo_caixa(session)
    context_header = Context.Header(
        pretitle='Registros',
        title='Vendas',
        symbol='shopping_cart',
        buttons=[
            Button(
                content='Excluír Selecionados',
                classname='btn',
                symbol='delete',
                attributes={
                    'disabled': 'true',
                    'data-bs-toggle': 'modal',
                    'id': 'btn-excluir-selecionados',
                    'data-bs-target': '#modalDelete',
                    'data-bs-payload': json.dumps({
                        'action': str(request.url_for('post_vendas_excluir')),
                        '.text-secondary': 'Excluir vendas selecionadas?'
                    }),
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
async def post_vendas_index(request: fastapi.Request, payload: inputs.VendaCriar = fastapi.Form(), session: Session = DBSESSAO_DEP):
    repository.create_venda(session, descricao=payload.descricao, valor=payload.valor)
    return redirect_back(request, message='Venda criada com sucesso!')


@router.post('/excluir', include_in_schema=False)
async def post_vendas_excluir(request: fastapi.Request, selecionados_ids: str = fastapi.Form(), session: Session = DBSESSAO_DEP):
    if selecionados_ids:
        for id in selecionados_ids.split(','):
            repository.delete_venda(session, id=int(id))
    return redirect_back(request, message='Venda excluída com sucesso!')


@router.post('/atualizar', include_in_schema=False)
async def post_vendas_atualizar(request: fastapi.Request, payload: inputs.VendaAtualizar = fastapi.Form(), session: Session = DBSESSAO_DEP):
    repository.update_venda(session, id=payload.id, descricao=payload.descricao, valor=payload.valor)
    return redirect_back(request, message='Venda atualizada com sucesso!')
