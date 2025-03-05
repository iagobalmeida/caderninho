import json

import fastapi
from sqlmodel import Session

from src import auth
from src.db import DBSESSAO_DEP
from src.domain import inputs, repository
from src.services import delete_entity, list_entity
from src.templates import render
from src.templates.context import Context
from src.utils import redirect_back, redirect_url_for

router = fastapi.APIRouter(prefix='/app/receitas', dependencies=[auth.HEADER_AUTH])


@router.get('/', include_in_schema=False)
async def get_receitas_index(request: fastapi.Request, page: int = fastapi.Query(1), filter_nome: str = None, db_session: Session = DBSESSAO_DEP):
    filters = {}
    if filter_nome:
        filters.update(nome=filter_nome)

    return await list_entity(
        request=request,
        db_session=db_session,
        entity=repository.Entities.RECEITA,
        page=page,
        table_modal=False,
        filters=filters
    )


@router.post('/', include_in_schema=False)
async def post_receitas_index(request: fastapi.Request, nome: str = fastapi.Form(), session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    db_receita = await repository.create(auth_session=auth_session, db_session=session, entity=repository.Entities.RECEITA, values={
        'nome': nome,
        'peso_unitario': 1,
        'procentagem_lucro': 33
    })
    return redirect_url_for(request, 'get_receita', id=db_receita.id)


@router.get('/{id}', include_in_schema=False)
async def get_receita(request: fastapi.Request, id: int, session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    db_receita, _, _ = await repository.get(auth_session=auth_session, db_session=session, entity=repository.Entities.RECEITA, filters={'id': id}, first=True)
    if not db_receita:
        return redirect_url_for(request, 'get_receitas_index', error=f'Receita #{id} não encontrada')
    context_header = Context.Header(
        pretitle='Registros',
        title='Receitas',
        symbol='library_books',
        buttons=[]
    )

    gastos = db_receita.gastos

    insumos_table_columns = [
        'Nome',
        'Quantidade (g)',
        'Custo/grama (R$)',
        'Custo Total (R$)',
        'Estoque Atual'
    ]
    insumos_table_data = [gasto for gasto in gastos if gasto.insumo_id]
    insumos_table_no_result = 'Nenhum registro encontrado'
    insumos_table_modal = '#atualizarReceitaInsumoModal'

    custos_table_columns = [
        'Descrição',
        'Tipo',
        'Valor'
    ]
    custos_table_data = [gasto for gasto in gastos if gasto.gasto_tipo]
    custos_table_no_result = 'Nenhum registro encontrado'
    custos_table_modal = '#atualizarReceitaGastoModal'

    return await render(
        session=session,
        request=request,
        template_name='receitas/detail.html',
        context={
            'header': context_header,
            'receita': db_receita,
            'insumos_table_columns': insumos_table_columns,
            'insumos_table_data': insumos_table_data,
            'insumos_table_no_result': insumos_table_no_result,
            'insumos_table_modal': insumos_table_modal,
            'custos_table_columns': custos_table_columns,
            'custos_table_data': custos_table_data,
            'custos_table_no_result': custos_table_no_result,
            'custos_table_modal': custos_table_modal
        }
    )


@router.post('/atualizar', include_in_schema=False)
async def post_receita_atualizar(request: fastapi.Request, payload: inputs.ReceitaAtualizar = fastapi.Form(), session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    await repository.update(
        auth_session=auth_session,
        db_session=session,
        entity=repository.Entities.RECEITA,
        filters={
            'id': payload.id
        },
        values={
            'nome': payload.nome,
            'peso_unitario': payload.peso_unitario,
            'porcentagem_lucro': payload.porcentagem_lucro
        }
    )
    return redirect_back(request, message='Receita atualizada com sucesso!')


@router.post('/excluir', include_in_schema=False)
async def post_receita_excluir(request: fastapi.Request, selecionados_ids: str = fastapi.Form(), session: Session = DBSESSAO_DEP):
    try:
        await delete_entity(
            request=request,
            db_session=session,
            entity=repository.Entities.RECEITA,
            ids=selecionados_ids.split(',')
        )
    except ValueError:
        pass
    return redirect_url_for(request, 'get_receitas_index', message='Receita excluída com sucesso!')


@router.post('/gastos/incluir', include_in_schema=False)
async def post_receita_gastos_incluir(request: fastapi.Request, payload: inputs.ReceitaGastosAdicionar = fastapi.Form(), session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    await repository.create(auth_session=auth_session, db_session=session, entity=repository.Entities.RECEITA_GASTO, values={
        'receita_id': payload.receita_id,
        'insumo_id': payload.insumo_id,
        'descricao': payload.descricao,
        'gasto_valor': payload.gasto_valor,
        'gasto_tipo': payload.gasto_tipo,
        'quantidade': payload.quantidade
    })
    return redirect_url_for(request, 'get_receita', id=payload.receita_id)


@router.post('/gastos/atualizar', include_in_schema=False)
async def post_receita_gastos_atualizar(request: fastapi.Request, payload: inputs.ReceitaGastosAtualizar = fastapi.Form(), session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    await repository.update(
        auth_session=auth_session,
        db_session=session,
        entity=repository.Entities.RECEITA_GASTO,
        filters={
            'id': payload.id
        },
        values={
            'quantidade': payload.quantidade
        }
    )
    if payload.insumo_nome:
        await repository.update(
            auth_session=auth_session,
            db_session=session,
            entity=repository.Entities.INSUMO,
            filters={
                'id': payload.insumo_id
            },
            values={
                'nome': payload.insumo_nome,
                'peso': payload.insumo_peso,
                'custo': payload.insumo_custo
            }
        )
    return redirect_url_for(request, 'get_receita', id=payload.receita_id)


@router.post('/gastos/remover', include_in_schema=False)
async def post_receita_gastos_remover(request: fastapi.Request, payload: inputs.ReceitaGastosRemover = fastapi.Form(), session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    if payload.selecionados_ids:
        for id in payload.selecionados_ids.split(','):
            await repository.delete(auth_session=auth_session, db_session=session, entity=repository.Entities.RECEITA_GASTO, filters={'id': id})
    return redirect_url_for(request, 'get_receita', id=payload.receita_id)
