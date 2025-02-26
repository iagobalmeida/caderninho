import fastapi
from sqlmodel import Session

from src import auth
from src.db import DBSESSAO_DEP
from src.domain import inputs, repository
from src.services import delete_entity, list_entity
from src.utils import redirect_back

router = fastapi.APIRouter(prefix='/app/vendas', dependencies=[auth.HEADER_AUTH])


@router.get('/', include_in_schema=False)
async def get_vendas_index(request: fastapi.Request, page: int = fastapi.Query(1), db_session: Session = DBSESSAO_DEP):
    return await list_entity(
        request=request,
        db_session=db_session,
        entity=repository.Entities.VENDA,
        page=page,
        filters={}
    )


@router.post('/', include_in_schema=False)
async def post_vendas_index(request: fastapi.Request, payload: inputs.VendaCriar = fastapi.Form(), session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    await repository.create(auth_session=auth_session, db_session=session, entity=repository.Entities.VENDA, values={
        'descricao': payload.descricao,
        'valor': payload.valor
    })
    return redirect_back(request, message='Venda criada com sucesso!')


@router.post('/excluir', include_in_schema=False)
async def post_venda_excluir(request: fastapi.Request, selecionados_ids: str = fastapi.Form(), db_session: Session = DBSESSAO_DEP):
    return await delete_entity(
        request=request,
        db_session=db_session,
        entity=repository.Entities.VENDA,
        ids=selecionados_ids.split(',')
    )


@router.post('/marcar/recebido', include_in_schema=False)
async def post_vendas_marcar_recebido(request: fastapi.Request, selecionados_ids: str = fastapi.Form(), session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    if selecionados_ids:
        for id in selecionados_ids.split(','):
            await repository.update(auth_session=auth_session, db_session=session, entity=repository.Entities.VENDA, filters={'id': id}, values={'recebido': True})
    return redirect_back(request, message='Venda(s) atualizada(s) com sucesso!')


@router.post('/marcar/pendente', include_in_schema=False)
async def post_vendas_marcar_pendente(request: fastapi.Request, selecionados_ids: str = fastapi.Form(), session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    if selecionados_ids:
        for id in selecionados_ids.split(','):
            await repository.update(auth_session=auth_session, db_session=session, entity=repository.Entities.VENDA, filters={'id': id}, values={'recebido': False})
    return redirect_back(request, message='Venda(s) atualizada(s) com sucesso!')


@router.post('/atualizar', include_in_schema=False)
async def post_vendas_atualizar(request: fastapi.Request, payload: inputs.VendaAtualizar = fastapi.Form(), session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    await repository.update(
        auth_session=auth_session,
        db_session=session,
        entity=repository.Entities.VENDA,
        filters={
            'id': payload.id
        },
        values={
            'descricao': payload.descricao,
            'valor': payload.valor,
            'recebido': True if payload.recebido else False
        }
    )
    return redirect_back(request, message='Venda atualizada com sucesso!')
