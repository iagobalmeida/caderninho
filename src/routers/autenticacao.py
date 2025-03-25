import fastapi

import auth
import db
from domain import inputs, repository
from utils import redirect_back

router = fastapi.APIRouter(prefix='/app/auth')


@router.post('/', include_in_schema=False)
async def post_index(request: fastapi.Request, email: str = fastapi.Form(), senha: str = fastapi.Form(), lembrar_de_mim: bool = fastapi.Form(False), session: db.AsyncSession = db.DBSESSAO_DEP):
    return await auth.request_login(session, request, email=email, senha=senha, lembrar_de_mim=lembrar_de_mim)


@router.post('/authenticate')
async def post_authenticate(request: fastapi.Request, email: str = fastapi.Form(), senha: str = fastapi.Form(), session: db.AsyncSession = db.DBSESSAO_DEP):
    return await auth.usuario_autenticar(session, request=request, email=email, senha=senha)


@router.get('/logout', include_in_schema=False)
async def get_logout(request: fastapi.Request):
    return await auth.request_logout(request)


@router.post('/perfil', dependencies=[auth.HEADER_AUTH])
async def post_perfil(request: fastapi.Request, payload: inputs.UsuarioAtualizar = fastapi.Form(),  session: db.AsyncSession = db.DBSESSAO_DEP):
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
    return redirect_back(request, message='Perfil atualizado com sucesso!')


@router.post('/atualizar_senha', include_in_schema=False)
async def post_atualizar_senha(request: fastapi.Request, payload: inputs.AtualizarSenha = fastapi.Form(),  session: db.AsyncSession = db.DBSESSAO_DEP):
    if payload.senha != payload.senha_confirmar:
        return redirect_back(request, error='As senhas não batem')

    auth_session = getattr(request.state, 'auth', None)
    await repository.update(
        auth_session=auth_session,
        db_session=session,
        entity=repository.Entities.USUARIO,
        filters={
            'id': payload.id
        },
        values={
            'senha': payload.senha
        }
    )
    return redirect_back(request, message='Senha alterada com sucesso!')
