import fastapi
from sqlmodel import Session

from src.db import SESSION_DEP
from src.decorators.auth import authorized
from src.domain import inputs, repository
from src.templates import render
from src.templates.context import Button, Context
from src.utils import redirect_back, redirect_url_for

router = fastapi.APIRouter(prefix='/receitas')
context_header = Context.Header(
    pretitle='Registros',
    title='Receitas',
    symbol='library_books',
    buttons=[
        Button(
            content='Apagar Selecionados',
            classname='btn',
            symbol='delete',
            attributes={
                'disabled': 'true',
                'data-bs-toggle': 'modal',
                'data-bs-target': '#modalDeleteReceita',
                'id': 'btn-apagar-selecionados'
            }
        ),
        Button(
            content='Criar Receita',
            classname='btn btn-success',
            symbol='add',
            attributes={
                'data-bs-toggle': 'modal',
                'data-bs-target': '#modalCreateReceita'
            }
        )
    ]
)


@router.post('/', include_in_schema=False)
@authorized
async def post_receitas_index(request: fastapi.Request, nome: str = fastapi.Form(), session: Session = SESSION_DEP):
    db_receita = repository.create_receita(session, nome)
    return redirect_url_for(request, 'get_receita', id=db_receita.id)


@router.get('/', include_in_schema=False)
@authorized
async def get_receitas_index(request: fastapi.Request, filter_nome: str = None, session: Session = SESSION_DEP):
    db_receitas = repository.list_receitas(session, filter_nome)
    return render(
        session=session,
        request=request,
        template_name='receitas/list.html',
        context={
            'header': context_header,
            'receitas': db_receitas,
            'filter_nome': filter_nome
        }
    )


@router.get('/{id}', include_in_schema=False)
@authorized
async def get_receita(request: fastapi.Request, id: int, session: Session = SESSION_DEP):
    db_receita = repository.get_receita(session, id)
    if not db_receita:
        raise ValueError(f'Receita com id {id} não encontrada')
    db_ingredientes = repository.get_ingredientes(session)
    header = context_header.copy()
    header['buttons'] = []
    return render(
        session=session,
        request=request,
        template_name='receitas/detail.html',
        context={
            'header': header,
            'receita': db_receita,
            'ingredientes': db_ingredientes
        }
    )


@router.post('/atualizar', include_in_schema=False)
@authorized
async def post_receita_atualizar(request: fastapi.Request, payload: inputs.ReceitaAtualizar = fastapi.Form(), session: Session = SESSION_DEP):
    repository.update_receita(
        session,
        id=payload.id,
        nome=payload.nome,
        peso_unitario=payload.peso_unitario,
        porcentagem_lucro=payload.porcentagem_lucro
    )
    return redirect_back(request)


@router.post('/deletar', include_in_schema=False)
@authorized
async def post_receita_deletar(request: fastapi.Request, selecionados_ids: str = fastapi.Form(), session: Session = SESSION_DEP):
    if selecionados_ids:
        for id in selecionados_ids.split(','):
            repository.delete_receita(session, id=id)
    return redirect_url_for(request, 'get_receitas_index')


@router.post('/ingredientes/incluir', include_in_schema=False)
@authorized
async def post_receita_ingredientes_incluir(request: fastapi.Request, payload: inputs.ReceitaIngredienteAdicionar = fastapi.Form(), session: Session = SESSION_DEP):
    repository.create_receita_ingrediente(session, receita_id=payload.receita_id, ingrediente_id=payload.ingrediente_id, quantidade=payload.quantidade)
    return redirect_url_for(request, 'get_receita', id=payload.receita_id)


@router.post('/ingredientes/atualizar', include_in_schema=False)
@authorized
async def post_receita_ingredientes_atualizar(request: fastapi.Request, payload: inputs.ReceitaIngredienteAtualizar = fastapi.Form(), session: Session = SESSION_DEP):
    repository.update_receita_ingrediente(session, id=payload.id, quantidade=payload.quantidade)
    if payload.ingrediente_nome:
        repository.update_ingrediente(session, id=payload.ingrediente_id, nome=payload.ingrediente_nome, custo=payload.ingrediente_custo, peso=payload.ingrediente_peso)
    return redirect_url_for(request, 'get_receita', id=payload.receita_id)


@router.post('/ingredientes/remover', include_in_schema=False)
@authorized
async def post_receita_ingredientes_remover(request: fastapi.Request, payload: inputs.ReceitaIngredienteRemover = fastapi.Form(), session: Session = SESSION_DEP):
    if payload.selecionados_ids:
        for id in payload.selecionados_ids.split(','):
            repository.delete_receita_ingrediente(session, id=int(id))
    return redirect_url_for(request, 'get_receita', id=payload.receita_id)
