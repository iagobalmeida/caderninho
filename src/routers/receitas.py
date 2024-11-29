import json

import fastapi
from sqlmodel import Session

from src import auth
from src.db import DBSESSAO_DEP
from src.domain import inputs, repository
from src.templates import render
from src.templates.context import Button, Context
from src.utils import redirect_back, redirect_url_for

router = fastapi.APIRouter(prefix='/receitas', dependencies=[auth.HEADER_AUTH])


@router.post('/', include_in_schema=False)
async def post_receitas_index(request: fastapi.Request, nome: str = fastapi.Form(), session: Session = DBSESSAO_DEP):
    db_receita = repository.create(session, repository.Entities.RECEITA, {
        'nome': nome,
        'peso_unitario': 1,
        'procentagem_lucro': 33
    })
    return redirect_url_for(request, 'get_receita', id=db_receita.id)


@router.get('/', include_in_schema=False)
async def get_receitas_index(request: fastapi.Request, filter_nome: str = None, session: Session = DBSESSAO_DEP):
    db_receitas = repository.get(session, repository.Entities.RECEITA, {'nome': filter_nome})
    context_header = Context.Header(
        pretitle='Registros',
        title='Receitas',
        symbol='library_books',
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
                        'action': str(request.url_for('post_receita_deletar')),
                        '.text-secondary': 'Excluir receitas selecionadas?'
                    }),
                }
            ),
            Button(
                content='Criar Receita',
                classname='btn btn-success',
                symbol='add',
                attributes={
                    'data-bs-toggle': 'modal',
                    'data-bs-target': '#modalCreateReceita'
                }
            )
        ]
    )

    table_columns = repository.Entities.RECEITA.value.columns()
    table_data = db_receitas
    table_no_result = 'Nenhum registro encontrado'
    # table_modal = '#modalEditReceita'

    return render(
        session=session,
        request=request,
        template_name='receitas/list.html',
        context={
            'header': context_header,
            'table_columns': table_columns,
            'table_data': table_data,
            'table_no_result': table_no_result,
            # 'table_modal': table_modal,
            'filter_nome': filter_nome
        }
    )


@router.get('/{id}', include_in_schema=False)
async def get_receita(request: fastapi.Request, id: int, session: Session = DBSESSAO_DEP):
    db_receita = repository.get(session, repository.Entities.RECEITA, {'id': id}, first=True)
    if not db_receita:
        raise ValueError(f'Receita com id {id} não encontrada')
    db_ingredientes = repository.get(session, repository.Entities.INGREDIENTE)
    context_header = Context.Header(
        pretitle='Registros',
        title='Receitas',
        symbol='library_books',
        buttons=[]
    )
    return render(
        session=session,
        request=request,
        template_name='receitas/detail.html',
        context={
            'header': context_header,
            'receita': db_receita,
            'ingredientes': db_ingredientes
        }
    )


@router.post('/atualizar', include_in_schema=False)
async def post_receita_atualizar(request: fastapi.Request, payload: inputs.ReceitaAtualizar = fastapi.Form(), session: Session = DBSESSAO_DEP):
    repository.update(
        session=session,
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


@router.post('/deletar', include_in_schema=False)
async def post_receita_deletar(request: fastapi.Request, selecionados_ids: str = fastapi.Form(), session: Session = DBSESSAO_DEP):
    if selecionados_ids:
        for id in selecionados_ids.split(','):
            repository.delete(session, repository.Entities.RECEITA, {'id': id})
    return redirect_url_for(request, 'get_receitas_index')


@router.post('/ingredientes/incluir', include_in_schema=False)
async def post_receita_ingredientes_incluir(request: fastapi.Request, payload: inputs.ReceitaIngredienteAdicionar = fastapi.Form(), session: Session = DBSESSAO_DEP):
    repository.create(session, repository.Entities.RECEITA_INGREDIENTE, {
        'receita_id': payload.receita_id,
        'ingrediente_id': payload.ingrediente_id,
        'quantidade': payload.quantidade
    })
    return redirect_url_for(request, 'get_receita', id=payload.receita_id)


@router.post('/ingredientes/atualizar', include_in_schema=False)
async def post_receita_ingredientes_atualizar(request: fastapi.Request, payload: inputs.ReceitaIngredienteAtualizar = fastapi.Form(), session: Session = DBSESSAO_DEP):
    repository.update(
        session=session,
        entity=repository.Entities.RECEITA_INGREDIENTE,
        filters={
            'id': payload.id
        },
        values={
            'quantidade': payload.quantidade
        }
    )
    if payload.ingrediente_nome:
        repository.update(
            session=session,
            entity=repository.Entities.INGREDIENTE,
            filters={
                'id': payload.ingrediente_id
            },
            values={
                'nome': payload.ingrediente_nome,
                'peso': payload.ingrediente_peso,
                'custo': payload.ingrediente_custo
            }
        )
    return redirect_url_for(request, 'get_receita', id=payload.receita_id)


@router.post('/ingredientes/remover', include_in_schema=False)
async def post_receita_ingredientes_remover(request: fastapi.Request, payload: inputs.ReceitaIngredienteRemover = fastapi.Form(), session: Session = DBSESSAO_DEP):
    if payload.selecionados_ids:
        for id in payload.selecionados_ids.split(','):
            repository.delete(session, repository.Entities.RECEITA_INGREDIENTE, {'id': id})
    return redirect_url_for(request, 'get_receita', id=payload.receita_id)
