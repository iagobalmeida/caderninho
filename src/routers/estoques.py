import fastapi
from sqlmodel import Session

from src.db import SESSION_DEP
from src.decorators.auth import authorized
from src.domain import inputs, repository
from src.templates import render
from src.templates.context import Button, Context
from src.utils import redirect_back

router = fastapi.APIRouter(prefix='/estoques')
context_header = Context.Header(
    pretitle='Registros',
    title='Estoque',
    symbol='inventory_2',
    buttons=[
        Button(
            content='Apagar Selecionados',
            classname='btn',
            symbol='delete',
            attributes={
                'disabled': 'true',
                'data-bs-toggle': 'modal',
                'data-bs-target': '#modalDeleteEstoque',
                'id': 'btn-apagar-selecionados'
            }
        ),
        Button(
            content='Criar Movimentação',
            classname='btn btn-success',
            symbol='add',
            attributes={
                'data-bs-toggle': 'modal',
                'data-bs-target': '#modalCreateEstoque'
            }
        )
    ]
)


@router.get('/', include_in_schema=False)
@authorized
async def get_estoques_index(request: fastapi.Request, filter_ingrediente_id: int = -1, filter_data_inicio: str = None, filter_data_final: str = None, session: Session = SESSION_DEP):
    db_estoques = repository.list_estoques(session, filter_ingrediente_id, filter_data_inicio, filter_data_final)
    db_ingredientes = repository.get_ingredientes(session)
    entradas, saidas, caixa = repository.get_fluxo_caixa(session)
    return render(
        session=session,
        request=request,
        template_name='estoques/list.html',
        context={
            'header': context_header,
            'estoques': db_estoques,
            'ingredientes': db_ingredientes,
            'entradas': entradas,
            'saidas': saidas,
            'caixa': caixa,
            'filter_ingrediente_id': filter_ingrediente_id,
            'filter_data_inicio': filter_data_inicio,
            'filter_data_final': filter_data_final
        }
    )


@router.post('/', include_in_schema=False)
@authorized
async def post_estoques_index(request: fastapi.Request, payload: inputs.EstoqueCriar = fastapi.Form(), session: Session = SESSION_DEP):
    if payload.descricao == 'Uso em Receita' and payload.receita_id:
        db_receita = repository.get_receita(session, payload.receita_id)
        for ingrediente_link in db_receita.ingrediente_links:
            quantidade = -1 * ingrediente_link.quantidade * float(payload.quantidade_receita)
            repository.create_estoque(
                session,
                descricao=payload.descricao,
                ingrediente_id=ingrediente_link.ingrediente_id,
                quantidade=quantidade,
                valor_pago=0
            )
    else:
        quantidade = float(payload.quantidade_ingrediente) if payload.quantidade_ingrediente else None
        if payload.descricao != 'Compra' and quantidade:
            quantidade = quantidade * -1
        if payload.descricao == 'Outros' and payload.descricao_customizada:
            payload.descricao = payload.descricao_customizada
        repository.create_estoque(
            session,
            descricao=payload.descricao,
            ingrediente_id=payload.ingrediente_id,
            quantidade=quantidade,
            valor_pago=float(payload.valor_pago) if payload.valor_pago else 0
        )
    return redirect_back(request)


@router.post('/excluir', include_in_schema=False)
@authorized
async def post_estoques_excluir(request: fastapi.Request, selecionados_ids: str = fastapi.Form(), session: Session = SESSION_DEP):
    if selecionados_ids:
        for id in selecionados_ids.split(','):
            repository.delete_estoque(session, id=int(id))
    return redirect_back(request)


@router.post('/atualizar', include_in_schema=False)
@authorized
async def post_estoques_atualizar(request: fastapi.Request, payload: inputs.EstoqueAtualizar = fastapi.Form(), session: Session = SESSION_DEP):
    repository.update_estoque(session, id=payload.id, descricao=payload.descricao, quantidade=payload.quantidade, valor_pago=payload.valor_pago)
    return redirect_back(request)
