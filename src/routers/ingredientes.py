import fastapi
from sqlmodel import Session

from db import SESSION_DEP
from domain import repository
from templates import render
from templates.context import Button, Context
from utils import redirect_back

router = fastapi.APIRouter(prefix='/ingredientes')
context_header = Context.Header(
    pretitle='Registros',
    title='Ingredientes',
    symbol='package_2',
    buttons=[
        Button(
            content='Novo Ingrediente',
            classname='btn btn-success',
            symbol='add',
            attributes={
                'data-bs-toggle': 'modal',
                'data-bs-target': '#novoIngredienteModal'
            }
        )
    ]
)


@router.get('/')
async def get_ingredientes_index(request: fastapi.Request, session: Session = SESSION_DEP):
    db_ingredientes = repository.get_ingredientes(session)
    return render(
        request=request,
        template_name='ingredientes/list.html',
        context={
            'header': context_header,
            'ingredientes': db_ingredientes
        }
    )


@router.post('/')
async def post_ingredientes_index(request: fastapi.Request, nome: str = fastapi.Form(), peso: float = fastapi.Form(), custo: float = fastapi.Form(), session: Session = SESSION_DEP):
    repository.create_ingrediente(session, nome=nome, peso=peso, custo=custo)
    return redirect_back(request)


@router.post('/editar')
async def post_ingredientes_editar(request: fastapi.Request, id: int = fastapi.Form(),  nome: str = fastapi.Form(), peso: float = fastapi.Form(), custo: float = fastapi.Form(), session: Session = SESSION_DEP):
    repository.update_ingrediente(session, id=id, nome=nome, peso=peso, custo=custo)
    return redirect_back(request)


@router.post('/excluir')
async def post_ingredientes_excluir(request: fastapi.Request, id: int = fastapi.Form(), session: Session = SESSION_DEP):
    repository.delete_ingrediente(session, id=id)
    return redirect_back(request)
