import json

import fastapi
from sqlmodel import Session

from src import auth
from src.db import DBSESSAO_DEP
from src.domain import inputs, repository
from src.templates import render
from src.templates.context import Button, Context
from src.utils import redirect_back

router = fastapi.APIRouter(prefix='/estoques', dependencies=[auth.HEADER_AUTH])


@router.get('/', include_in_schema=False)
async def get_estoques_index(request: fastapi.Request, filter_ingrediente_id: int = -1, filter_data_inicio: str = None, filter_data_final: str = None, session: Session = DBSESSAO_DEP):
    filters = {}
    if filter_data_inicio:
        filter.update(data_inicio=filter_data_inicio)
    if filter_data_final:
        filter.update(data_final=filter_data_final)
    if filter_ingrediente_id:
        filters.update(ingrediente_id=filter_ingrediente_id)

    db_estoques = repository.get(session, repository.Entities.ESTOQUE, filters=filters, order_by='data_criacao', desc=True)

    db_ingredientes = repository.get(session, repository.Entities.INGREDIENTE)
    entradas, saidas, caixa = repository.get_fluxo_caixa(session)

    context_header = Context.Header(
        pretitle='Registros',
        title='Estoque',
        symbol='inventory_2',
        buttons=[
            Button(
                content='Excluír Selecionados',
                classname='btn',
                symbol='delete',
                attributes={
                    'id': 'btn-excluir-selecionados',
                    'disabled': 'true',
                    'data-bs-toggle': 'modal',
                    'data-bs-target': '#modalConfirm',
                    'data-bs-payload': json.dumps({
                        'action': str(request.url_for('post_estoques_excluir')),
                        '.text-secondary': 'Excluir movimentações selecionadas?'
                    })
                }
            ),
            Button(
                content='Criar Movimentação',
                classname='btn btn-success',
                symbol='add',
                attributes={
                    'data-bs-toggle': 'modal',
                    'data-bs-target': '#modalCreateEstoque'
                }
            )
        ]
    )

    table_columns = repository.Entities.ESTOQUE.value.columns()
    table_data = db_estoques
    table_no_result = 'Nenhum registro encontrado'
    table_modal = '#modalEditEstoque'

    return render(
        session=session,
        request=request,
        template_name='list.html',
        context={
            'header': context_header,
            'table_columns': table_columns,
            'table_data': table_data,
            'table_no_result': table_no_result,
            'table_modal': table_modal,
            'ingredientes': db_ingredientes,
            'entradas': entradas,
            'saidas': saidas,
            'caixa': caixa,
            'filter_ingrediente_id': filter_ingrediente_id,
            'filter_data_inicio': filter_data_inicio,
            'filter_data_final': filter_data_final
        }
    )


@ router.post('/', include_in_schema=False)
async def post_estoques_index(request: fastapi.Request, payload: inputs.EstoqueCriar = fastapi.Form(), session: Session = DBSESSAO_DEP):
    if payload.descricao == 'Uso em Receita' and payload.receita_id:
        db_receita = repository.get(session, repository.Entities.RECEITA, {'id': id}, first=True)
        for ingrediente_link in db_receita.ingrediente_links:
            quantidade = -1 * ingrediente_link.quantidade * float(payload.quantidade_receita)
            repository.create(session, repository.Entities.ESTOQUE, {
                'descricao': payload.descricao,
                'ingrediente_id': ingrediente_link.ingrediente_id,
                'quantidade': quantidade,
                'valor_pago': 0
            })
    else:
        quantidade = float(payload.quantidade_ingrediente) if payload.quantidade_ingrediente else None
        if payload.descricao != 'Compra' and quantidade:
            quantidade = quantidade * -1
        if payload.descricao == 'Outros' and payload.descricao_customizada:
            payload.descricao = payload.descricao_customizada
        repository.create(session, repository.Entities.ESTOQUE, {
            'descricao': payload.descricao,
            'ingrediente_id': payload.ingrediente_id,
            'quantidade': quantidade,
            'valor_pago': float(payload.valor_pago) if payload.valor_pago else 0
        })
    return redirect_back(request, message='Movimentação criada com sucesso!')


@ router.post('/excluir', include_in_schema=False)
async def post_estoques_excluir(request: fastapi.Request, selecionados_ids: str = fastapi.Form(), session: Session = DBSESSAO_DEP):
    selecionados_ids = selecionados_ids.split(',')
    for id in selecionados_ids:
        repository.delete(session, repository.Entities.ESTOQUE, {'id': id})
    return redirect_back(request, message=f'{len(selecionados_ids)} registros excluídos com sucesso!')


@ router.post('/atualizar', include_in_schema=False)
async def post_estoques_atualizar(request: fastapi.Request, payload: inputs.EstoqueAtualizar = fastapi.Form(), session: Session = DBSESSAO_DEP):
    repository.update(
        session=session,
        entity=repository.Entities.ESTOQUE,
        filters={
            'id': payload.id
        },
        values={
            'descricao':  payload.descricao,
            'valor_pago':  payload.valor_pago,
            'quantidade':  payload.quantidade,
            'ingrediente_id':  payload.ingrediente_id
        }
    )
    return redirect_back(request, message='Movimentação atualizada com sucesso!')
