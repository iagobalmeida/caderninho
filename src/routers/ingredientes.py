import fastapi
from sqlmodel import Session

from src import auth
from src.db import DBSESSAO_DEP
from src.domain import inputs, repository
from src.templates import render
from src.templates.context import Button, Context
from src.utils import redirect_back

router = fastapi.APIRouter(prefix='/ingredientes', dependencies=[auth.HEADER_AUTH])
context_header = Context.Header(
    pretitle='Registros',
    title='Ingredientes',
    symbol='package_2',
    buttons=[
        Button(
            content='Excluír Selecionados',
            classname='btn',
            symbol='delete',
            attributes={
                'disabled': 'true',
                'data-bs-toggle': 'modal',
                'data-bs-target': '#modalDeleteIngrediente',
                'id': 'btn-excluir-selecionados'
            }
        ),
        Button(
            content='Criar Ingrediente',
            classname='btn btn-success',
            symbol='add',
            attributes={
                'data-bs-toggle': 'modal',
                'data-bs-target': '#modalCreateIngrediente'
            }
        )
    ]
)


@router.get('/', include_in_schema=False)
async def get_ingredientes_index(request: fastapi.Request, session: Session = DBSESSAO_DEP):
    db_ingredientes = repository.get(session, repository.Entities.INGREDIENTE)

    table_columns = repository.Entities.INGREDIENTE.value.columns()
    table_data = db_ingredientes
    table_no_result = 'Nenhum registro encontrado'
    table_modal = '#modalEditIngrediente'

    return render(
        session=session,
        request=request,
        template_name='list.html',
        context={
            'header': context_header,
            'table_columns': table_columns,
            'table_data': table_data,
            'table_no_result': table_no_result,
            'table_modal': table_modal
        }
    )


@router.post('/', include_in_schema=False)
async def post_ingredientes_index(request: fastapi.Request, payload: inputs.IngredienteCriar = fastapi.Form(), session: Session = DBSESSAO_DEP):
    repository.create(session, repository.Entities.INGREDIENTE, {
        'nome': payload.nome,
        'peso': payload.peso,
        'custo': payload.custo
    })
    return redirect_back(request, message='Ingrediente criado com sucesso!')


@router.post('/atualizar', include_in_schema=False)
async def post_ingredientes_atualizar(request: fastapi.Request, payload: inputs.IngredienteAtualizar = fastapi.Form(), session: Session = DBSESSAO_DEP):
    repository.update(
        session=session,
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
    return redirect_back(request, message='Ingrediente atualizado com sucesso!')


@router.post('/excluir', include_in_schema=False)
async def post_ingredientes_excluir(request: fastapi.Request, id: int = fastapi.Form(), session: Session = DBSESSAO_DEP):
    repository.delete(session, repository.Entities.RECEITA_INGREDIENTE, {'ingrediente_id': id})
    repository.delete(session, repository.Entities.INGREDIENTE, {'id': id})
    return redirect_back(request, message='Ingrediente excluído com sucesso!')
