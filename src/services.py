import json
from typing import List

import fastapi
import fastapi.security
from sqlmodel import Session

from src.domain import repository
from src.templates import render
from src.templates.context import Button, Context
from src.utils import redirect_back

ENTITY_SYMBOLS = {
    'Estoque': 'inventory_2',
    'Insumo': 'package_2'
}


def list_entity(request: fastapi.Request, db_session: Session, entity: repository.Entities, page: int = 1, filters: dict = {}):
    auth_session = getattr(request.state, 'auth', None)
    title = entity.value.__name__.title()

    order_by = None
    desc = False
    if hasattr(entity, 'data_criacao'):
        order_by = 'data_criacao'
        desc = True

    entities, pages, count = repository.get(
        auth_session=auth_session,
        db_session=db_session,
        entity=entity,
        filters=filters,
        order_by=order_by,
        page=page,
        desc=desc
    )

    table_columns = entity.value.columns()
    table_data = entities
    table_no_result = 'Nenhum registro encontrado'
    table_modal = f'#modalEdit{title}'

    delete_url = str(request.url_for(f'post_{title.lower()}_excluir'))

    context_header = Context.Header(
        pretitle='Registros',
        title=title,
        symbol=ENTITY_SYMBOLS.get(title, 'star'),
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
                        'action': delete_url,
                        '.text-secondary': f'Excluir {title}(s) selecionadas?'
                    })
                }
            ),
            Button(
                content=f'Criar {title}',
                classname='btn btn-success',
                symbol='add',
                attributes={
                    'data-bs-toggle': 'modal',
                    'data-bs-target': f'#modalCreate{title}'
                }
            )
        ]
    )

    db_insumos, _, _ = repository.get(auth_session=auth_session, db_session=db_session, entity=repository.Entities.INSUMO)
    entradas, saidas, caixa = repository.get_fluxo_caixa(auth_session=auth_session, db_session=db_session)

    return render(
        session=db_session,
        request=request,
        template_name='layout/list.html',
        context={
            'header': context_header,
            'table_columns': table_columns,
            'table_data': table_data,
            'table_no_result': table_no_result,
            'table_modal': table_modal,
            'table_pages': pages,
            'table_count': count,
            'insumos': db_insumos,
            'entradas': entradas,
            'saidas': saidas,
            'caixa': caixa,
            'filter_insumo_id': filters.get('insumo_id', None),
            'filter_data_inicio': filters.get('data_inicio', None),
            'filter_data_final': filters.get('data_final', None)
        }
    )


def delete_entity(request: fastapi.Request, db_session: Session, entity: repository.Entities, ids: List[int]):
    auth_session = getattr(request.state, 'auth', None)
    for id in ids:
        repository.delete(auth_session=auth_session, db_session=db_session, entity=entity, filters={'id': id})
    return redirect_back(request, message=f'{len(ids)} registros excluídos com sucesso!')
