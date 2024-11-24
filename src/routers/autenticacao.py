import fastapi

from src import auth, db
from src.domain import inputs, repository
from src.utils import redirect_back

router = fastapi.APIRouter(prefix='/auth')


@router.post('/', include_in_schema=False)
async def post_index(request: fastapi.Request, email: str = fastapi.Form(), senha: str = fastapi.Form(), session: auth.DBSessaoAutenticada = db.DBSESSAO_DEP):
    return auth.request_login(session, request, email=email, senha=senha)


@router.post('/authenticate')
async def post_authenticate(email: str = fastapi.Form(), senha: str = fastapi.Form(), session: auth.DBSessaoAutenticada = db.DBSESSAO_DEP):
    return auth.usuario_autenticar(session, email=email, senha=senha)


@router.get('/logout', include_in_schema=False)
async def get_logout(request: fastapi.Request):
    return auth.request_logout(request)


@router.post('/perfil', dependencies=[auth.HEADER_AUTH])
async def post_perfil(request: fastapi.Request, payload: inputs.UsuarioAtualizar = fastapi.Form(),  session: auth.DBSessaoAutenticada = db.DBSESSAO_DEP):
    repository.update_organizacao_usuario(session, id=payload.id, nome=payload.nome, email=payload.email, dono=payload.dono)
    return redirect_back(request, message='Perfil atualizado com sucesso!')


@router.post('/atualizar_senha', include_in_schema=False)
async def post_atualizar_senha(request: fastapi.Request, payload: inputs.AtualizarSenha = fastapi.Form(),  session: auth.DBSessaoAutenticada = db.DBSESSAO_DEP):
    repository.update_usuario_senha(session, id=payload.id, senha_atual=payload.senha_atual, senha=payload.senha, senha_confirmar=payload.senha_confirmar)
    return redirect_back(request, message='Senha alterada com sucesso!')
