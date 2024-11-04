import fastapi
from sqlmodel import Session

from db import SESSION_DEP
from domain import repository
from templates import render
from templates.context import Button, Context
from utils import redirect_back, redirect_url_for

router = fastapi.APIRouter(prefix='/receitas')
context_header = Context.Header(
    pretitle='Registros',
    title='Receitas',
    symbol='library_books',
    buttons=[
        Button(
            content='Nova Receita',
            classname='btn btn-success',
            symbol='add',
            attributes={
                'data-bs-toggle': 'modal',
                'data-bs-target': '#novaReceitaModal'
            }
        )
    ]
)


@router.post('/')
async def post_receitas_index(request: fastapi.Request, nome: str = fastapi.Form(), session: Session = SESSION_DEP):
    nova_receita = repository.create_receita(session, nome)
    return redirect_url_for(request, 'get_receita', id=nova_receita.id)


@router.get('/')
async def get_receitas_index(request: fastapi.Request, session: Session = SESSION_DEP):
    db_receitas = repository.get_receitas(session)
    return render(
        request=request,
        template_name='receitas/list.html',
        context={
            'header': context_header,
            'receitas': db_receitas
        }
    )


@router.get('/{id}')
async def get_receita(request: fastapi.Request, id: int, session: Session = SESSION_DEP):
    db_receita = repository.get_receita(session, id)
    if not db_receita:
        raise ValueError(f'Receita com id {id} não encontrada')
    db_ingredientes = repository.get_ingredientes(session)
    return render(
        request=request,
        template_name='receitas/detail.html',
        context={
            'header': context_header,
            'receita': db_receita,
            'ingredientes': db_ingredientes
        }
    )


@router.post('/atualizar')
async def post_receita_atualizar(request: fastapi.Request, id: int = fastapi.Form(), nome: str = fastapi.Form(), peso_unitario: float = fastapi.Form(), porcentagem_lucro: float = fastapi.Form(), session: Session = SESSION_DEP):
    repository.update_receita(session, id=id, nome=nome, peso_unitario=peso_unitario, porcentagem_lucro=porcentagem_lucro)
    return redirect_back(request)


@router.post('/deletar')
async def post_receita_deletar(id: int = fastapi.Form(), session: Session = SESSION_DEP):
    repository.delete_receita(session, id=id)
    return redirect_url_for('get_index')


@router.post('/{id}/ingredientes/incluir')
async def post_receita_ingredientes_incluir(request: fastapi.Request, id: int, ingrediente_id: int = fastapi.Form(), quantidade: float = fastapi.Form(), session: Session = SESSION_DEP):
    repository.create_receita_ingrediente(session, receita_id=id, ingrediente_id=ingrediente_id, quantidade=quantidade)
    return redirect_url_for(request, 'get_receita', id=id)


@router.post('/{receita_id}/ingredientes/atualizar')
async def post_receita_ingredientes_atualizar(request: fastapi.Request, receita_id: int, id: int = fastapi.Form(), quantidade: float = fastapi.Form(), session: Session = SESSION_DEP):
    repository.update_receita_ingrediente(session, id=id, quantidade=quantidade)
    return redirect_url_for(request, 'get_receita', id=receita_id)


@router.post('/{receita_id}/ingredientes/remover')
async def post_receita_ingredientes_remover(request: fastapi.Request, receita_id: int, id: int = fastapi.Form(), session: Session = SESSION_DEP):
    repository.delete_receita_ingrediente(session, id)
    return redirect_url_for(request, 'get_receita', id=receita_id)
