import fastapi

from src import auth, db
from src.domain import inputs, repository
from src.utils import redirect_back

router = fastapi.APIRouter(prefix='/auth')


@router.post('/', include_in_schema=False)
async def post_index(request: fastapi.Request, email: str = fastapi.Form(), senha: str = fastapi.Form(), lembrar_de_mim: bool = fastapi.Form(False), session: auth.DBSessaoAutenticada = db.DBSESSAO_DEP):
    return auth.request_login(session, request, email=email, senha=senha, lembrar_de_mim=lembrar_de_mim)


@router.post('/authenticate')
async def post_authenticate(email: str = fastapi.Form(), senha: str = fastapi.Form(), session: auth.DBSessaoAutenticada = db.DBSESSAO_DEP):
    return auth.usuario_autenticar(session, email=email, senha=senha)


@router.get('/logout', include_in_schema=False)
async def get_logout(request: fastapi.Request):
    return auth.request_logout(request)


@router.post('/perfil', dependencies=[auth.HEADER_AUTH])
async def post_perfil(request: fastapi.Request, payload: inputs.UsuarioAtualizar = fastapi.Form(),  session: auth.DBSessaoAutenticada = db.DBSESSAO_DEP):
    repository.update(
        session=session,
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
async def post_atualizar_senha(request: fastapi.Request, payload: inputs.AtualizarSenha = fastapi.Form(),  session: auth.DBSessaoAutenticada = db.DBSESSAO_DEP):
    if payload.senha != payload.senha_confirmar:
        raise ValueError('As senhas não batem')

    repository.update(
        session=session,
        entity=repository.Entities.USUARIO,
        filters={
            'id': payload.id
        },
        values={
            'senha': payload.senha
        }
    )
    return redirect_back(request, message='Senha alterada com sucesso!')
