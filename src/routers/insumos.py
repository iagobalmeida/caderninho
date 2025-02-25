import json

import fastapi
from sqlmodel import Session

from src import auth
from src.db import DBSESSAO_DEP
from src.domain import inputs, repository
from src.templates import render
from src.templates.context import Button, Context
from src.utils import redirect_back

router = fastapi.APIRouter(prefix='/app/insumos', dependencies=[auth.HEADER_AUTH])


@router.get('/', include_in_schema=False)
async def get_insumos_index(request: fastapi.Request, session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    db_insumos, db_insumos_pages, db_insumos_count = repository.get(auth_session=auth_session, db_session=session, entity=repository.Entities.INGREDIENTE)

    table_columns = repository.Entities.INGREDIENTE.value.columns()
    table_data = db_insumos
    table_no_result = 'Nenhum registro encontrado'
    table_modal = '#modalEditInsumo'

    context_header = Context.Header(
        pretitle='Registros',
        title='Insumos',
        symbol='package_2',
        buttons=[
            Button(
                content='Excluír Selecionados',
                classname='btn',
                symbol='delete',
                attributes={
                    'disabled': 'true',
                    'data-bs-toggle': 'modal',
                    'data-bs-target': '#modalConfirm',
                    'data-bs-payload': json.dumps({
                        'action': str(request.url_for('post_insumos_excluir')),
                        '.text-secondary': 'Excluir insumos selecionados?'
                    }),
                    'id': 'btn-excluir-selecionados'
                }
            ),
            Button(
                content='Criar Insumo',
                classname='btn btn-success',
                symbol='add',
                attributes={
                    'data-bs-toggle': 'modal',
                    'data-bs-target': '#modalCreateInsumo'
                }
            )
        ]
    )

    return render(
        session=session,
        request=request,
        template_name='layout/list.html',
        context={
            'header': context_header,
            'table_columns': table_columns,
            'table_data': table_data,
            'table_no_result': table_no_result,
            'table_modal': table_modal,
            'table_pages': db_insumos_pages,
            'table_count': db_insumos_count,
        }
    )


@router.post('/', include_in_schema=False)
async def post_insumos_index(request: fastapi.Request, payload: inputs.InsumoCriar = fastapi.Form(), session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    repository.create(auth_session=auth_session, db_session=session, entity=repository.Entities.INGREDIENTE, values={
        'nome': payload.nome,
        'peso': payload.peso,
        'custo': payload.custo,
        'unidade': payload.unidade
    })
    return redirect_back(request, message='Insumo criado com sucesso!')


@router.post('/atualizar', include_in_schema=False)
async def post_insumos_atualizar(request: fastapi.Request, payload: inputs.InsumoAtualizar = fastapi.Form(), session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    repository.update(
        auth_session=auth_session,
        db_session=session,
        entity=repository.Entities.INGREDIENTE,
        filters={
            'id': payload.id
        },
        values={
            'nome': payload.nome,
            'peso': payload.peso,
            'custo': payload.custo
        }
    )
    return redirect_back(request, message='Insumo atualizado com sucesso!')


@router.post('/excluir', include_in_schema=False)
async def post_insumos_excluir(request: fastapi.Request, selecionados_ids: str = fastapi.Form(), session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    selecionados_ids = selecionados_ids.split(',')
    for id in selecionados_ids:
        try:
            repository.delete(auth_session=auth_session, db_session=session, entity=repository.Entities.RECEITA_INGREDIENTE, filters={'insumo_id': id})
        except ValueError:
            pass
        repository.delete(auth_session=auth_session, db_session=session, entity=repository.Entities.INGREDIENTE, filters={'id': id})
    return redirect_back(request, message=f'{len(selecionados_ids)} insumos excluídos com sucesso!')
