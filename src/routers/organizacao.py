import fastapi
from sqlmodel import Session

import auth
from db import DBSESSAO_DEP
from domain import inputs, repository
from templates import render
from templates.context import Context
from utils import redirect_back

router = fastapi.APIRouter(prefix='/app/organizacao', dependencies=[auth.HEADER_AUTH])
context_header = Context.Header(
    pretitle='Organização',
    title='Organização',
    symbol='library_books',
    buttons=[]
)


@router.get('/', include_in_schema=False)
async def get_organizacao_index(request: fastapi.Request, session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    if auth_session.organizacao_descricao:
        context_header['title'] = auth_session.organizacao_descricao

    db_organizacao, _, _ = await repository.get(auth_session=auth_session, db_session=session, entity=repository.Entities.ORGANIZACAO, filters={'id': auth_session.organizacao_id}, first=True)
    db_usuarios, _, _ = await repository.get(auth_session=auth_session, db_session=session, entity=repository.Entities.USUARIO)
    db_gastos_fixos, _, _ = await repository.get(auth_session=auth_session, db_session=session, entity=repository.Entities.GASTO_RECORRENTE)

    return await render(
        session=session,
        request=request,
        template_name='organizacao/detail.html',
        context={
            'header': context_header,
            'organizacao': db_organizacao,
            'usuarios': db_usuarios,
            'gastos_fixos': db_gastos_fixos
        }
    )


@router.post('/', include_in_schema=False)
async def post_organizacao_index(request: fastapi.Request, id: str = fastapi.Form(), descricao: str = fastapi.Form(), cidade: str = fastapi.Form(), chave_pix: str = fastapi.Form(), session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    await repository.update(
        auth_session=auth_session,
        db_session=session,
        entity=repository.Entities.ORGANIZACAO,
        filters={
            'id': id
        },
        values={
            'descricao': descricao,
            'cidade': cidade,
            'chave_pix': chave_pix
        }
    )
    return redirect_back(request, message='Organização atualizada com sucesso!')


@router.post('/configuracoes', include_in_schema=False)
async def post_organizacao_configuracoes(request: fastapi.Request, id: str = fastapi.Form(), converter_kg: bool = fastapi.Form(False), converter_kg_sempre: bool = fastapi.Form(False), usar_custo_med: bool = fastapi.Form(False), session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    await repository.update(
        auth_session=auth_session,
        db_session=session,
        entity=repository.Entities.ORGANIZACAO,
        filters={
            'id': id
        },
        values={
            'configuracoes': {
                'converter_kg': converter_kg,
                'converter_kg_sempre': converter_kg_sempre,
                'usar_custo_med': usar_custo_med
            }
        }
    )
    return redirect_back(request, message='Organização atualizada com sucesso!')


@router.post('/gastos_recorrentes/criar', include_in_schema=False)
async def post_organizacao_gastos_recorrentes_criar(request: fastapi.Request, payload: inputs.GastoRecorrenteCriar = fastapi.Form(), session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    await repository.create(auth_session=auth_session, db_session=session, entity=repository.Entities.GASTO_RECORRENTE, values={
        'organizacao_id': payload.organizacao_id,
        'descricao': payload.descricao,
        'data_inicio': payload.data_inicio,
        'valor': payload.valor,
        'tipo': payload.tipo,
        'recorrencia': payload.recorrencia
    })
    return redirect_back(request, message='Gasto Recorrente criado com sucesso!')


@router.post('/gastos_recorrentes/excluir', include_in_schema=False)
async def post_organizacao_gastos_recorrentes_excluir(request: fastapi.Request, selecionados_ids: str = fastapi.Form(), session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    if selecionados_ids:
        for id in selecionados_ids.split(','):
            await repository.delete(auth_session=auth_session, db_session=session, entity=repository.Entities.GASTO_RECORRENTE, filters={'id': int(id)})
    return redirect_back(request, message='Gasto Recorrente excluído com sucesso!')


@router.post('/usuarios/criar', include_in_schema=False)
async def post_organizacao_usuarios_criar(request: fastapi.Request, payload: inputs.UsuarioCriar = fastapi.Form(), session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    if payload.senha != payload.senha_confirmar:
        return redirect_back(request, error='As senhas não batem')

    # if not payload.organizacao_id:
    #     db_organizacao = await repository.create(session, repository.Entities.ORGANIZACAO, {'descricao': payload.organizacao_descricao})
    #     payload.organizacao_id = db_organizacao.id

    await repository.create(auth_session=auth_session, db_session=session, entity=repository.Entities.USUARIO, values={
        'nome': payload.nome,
        'email': payload.email,
        'senha': payload.senha,
        'organizacao_id': payload.organizacao_id,
        'dono': payload.dono
    })
    return redirect_back(request, message='Usuário criado com sucesso!')


@router.post('/usuarios/editar', include_in_schema=False)
async def post_organizacao_usuarios_editar(request: fastapi.Request, payload: inputs.UsuarioEditar = fastapi.Form(), session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    await repository.update(
        auth_session=auth_session,
        db_session=session,
        entity=repository.Entities.USUARIO,
        filters={
            'id': payload.id
        },
        values={
            'nome': payload.nome,
            'email': payload.email,
            'dono': payload.dono,
            'senha': payload.senha
        }
    )
    return redirect_back(request, message='Usuário atualizado com sucesso!')


@router.post('/usuarios/excluir', include_in_schema=False)
async def post_organizacao_usuarios_excluir(request: fastapi.Request, selecionados_ids: str = fastapi.Form(), session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    if selecionados_ids:
        for id in selecionados_ids.split(','):
            await repository.delete(auth_session=auth_session, db_session=session, entity=repository.Entities.USUARIO, filters={'id': int(id)})
    return redirect_back(request, message='Usuário excluído com sucesso!')


@router.get('/sistema/recarregar', include_in_schema=False)
async def post_organizacao_sistema_recarregar(request: fastapi.Request, session: Session = DBSESSAO_DEP):
    auth_session = getattr(request.state, 'auth', None)
    await repository.recarregar_cache(auth_session=auth_session, db_session=session)
    return redirect_back(request, message='Sistema recarregado com sucesso!')
