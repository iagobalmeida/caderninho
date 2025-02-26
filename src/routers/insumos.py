
import fastapi
from sqlmodel import Session

from src import auth
from src.db import DBSESSAO_DEP
from src.domain import inputs, repository
from src.services import delete_entity, list_entity
from src.utils import redirect_back

router = fastapi.APIRouter(prefix='/app/insumos', dependencies=[auth.HEADER_AUTH])


@router.get('/', include_in_schema=False)
async def get_insumos_index(request: fastapi.Request, page: int = fastapi.Query(1),  db_session: Session = DBSESSAO_DEP):
    return await list_entity(
        request=request,
        db_session=db_session,
        entity=repository.Entities.INSUMO,
        page=page,
        filters={}
    )


@router.post('/', include_in_schema=False)
async def post_insumos_index(request: fastapi.Request, payload: inputs.InsumoCriar = fastapi.Form(), session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    await repository.create(auth_session=auth_session, db_session=session, entity=repository.Entities.INSUMO, values={
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
        entity=repository.Entities.INSUMO,
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
async def post_insumo_excluir(request: fastapi.Request, selecionados_ids: str = fastapi.Form(), session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    selecionados_ids = selecionados_ids.split(',')
    for id in selecionados_ids:
        try:
            await repository.delete(auth_session=auth_session, db_session=session, entity=repository.Entities.RECEITA_INGREDIENTE, filters={'insumo_id': id})
        except ValueError:
            pass
    return await delete_entity(
        request=request,
        db_session=session,
        entity=repository.Entities.INSUMO,
        ids=selecionados_ids
    )
