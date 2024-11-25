import fastapi
from sqlmodel import Session

from src import auth
from src.db import DBSESSAO_DEP
from src.domain import inputs, repository
from src.templates import render
from src.templates.context import Context
from src.utils import redirect_back

router = fastapi.APIRouter(prefix='/organizacao', dependencies=[auth.HEADER_AUTH])
context_header = Context.Header(
    pretitle='Organização',
    title='Organização',
    symbol='library_books',
    buttons=[]
)


@router.get('/', include_in_schema=False)
async def get_organizacao_index(request: fastapi.Request, session: auth.DBSessaoAutenticada = DBSESSAO_DEP):
    usuario = session.sessao_autenticada
    context_header['title'] = usuario.organizacao_descricao

    db_usuarios = repository.get_usuarios(session)
    db_organizacao = repository.get_organizacao(session, usuario.organizacao_id)

    return render(
        session=session,
        request=request,
        template_name='organizacao/detail.html',
        context={
            'header': context_header,
            'usuarios': db_usuarios,
            'organizacao': db_organizacao
        }
    )


@router.post('/', include_in_schema=False)
async def post_organizacao_index(request: fastapi.Request, id: int = fastapi.Form(), descricao: str = fastapi.Form(), cidade: str = fastapi.Form(), chave_pix: str = fastapi.Form(), session: Session = DBSESSAO_DEP):
    repository.update_organizacao(session, id, descricao, cidade, chave_pix)
    return redirect_back(request, message='Organização atualizada com sucesso!')


@router.post('/usuarios/criar', include_in_schema=False)
async def post_organizacao_usuarios_criar(request: fastapi.Request, payload: inputs.UsuarioCriar = fastapi.Form(), session: Session = DBSESSAO_DEP):
    if payload.senha != payload.senha_confirmar:
        raise ValueError('As senhas não batem')
    repository.create_usuario(session, nome=payload.nome, email=payload.email, senha=payload.senha,
                              organizacao_descricao=payload.organizacao_descricao, organizacao_id=payload.organizacao_id, dono=payload.dono)
    return redirect_back(request, message='Usuário criado com sucesso!')


@router.post('/usuarios/editar', include_in_schema=False)
async def post_organizacao_usuarios_editar(request: fastapi.Request, payload: inputs.UsuarioEditar = fastapi.Form(), session: Session = DBSESSAO_DEP):
    if payload.nova_senha:
        repository.update_organizacao_usuario(session, id=payload.id, nome=payload.nome, email=payload.email, senha=payload.nova_senha, dono=payload.dono)
    else:
        repository.update_organizacao_usuario(session, id=payload.id, nome=payload.nome, email=payload.email, dono=payload.dono)
    return redirect_back(request, message='Usuário atualizado com sucesso!')


@router.post('/usuarios/excluir', include_in_schema=False)
async def post_organizacao_usuarios_excluir(request: fastapi.Request, selecionados_ids: str = fastapi.Form(), session: Session = DBSESSAO_DEP):
    if selecionados_ids:
        for id in selecionados_ids.split(','):
            repository.delete_usuario(session, id=int(id))
    return redirect_back(request, message='Usuário excluído com sucesso!')
