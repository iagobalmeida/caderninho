import csv
import io
from uuid import UUID

import fastapi
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from caderninho.src import auth
from caderninho.src.db import DBSESSAO_DEP
from caderninho.src.domain import inputs, repository
from caderninho.src.templates import render
from caderninho.src.templates.context import Context
from caderninho.src.utils import csv_parse, csv_response, redirect_back

router = fastapi.APIRouter(prefix="/app/organizacao", dependencies=[auth.HEADER_AUTH])
context_header = Context.Header(
    pretitle="Organização", title="Organização", symbol="library_books", buttons=[]
)


@router.get("/", include_in_schema=False)
async def get_organizacao_index(
    request: fastapi.Request, session: Session = DBSESSAO_DEP
):
    auth_session = getattr(request.state, "auth", None)
    if auth_session.organizacao_descricao:
        context_header["title"] = auth_session.organizacao_descricao

    db_organizacao, _, _ = await repository.get(
        auth_session=auth_session,
        db_session=session,
        entity=repository.Entities.ORGANIZACAO,
        filters={"id": auth_session.organizacao_id},
        first=True,
    )
    db_usuarios, _, _ = await repository.get(
        auth_session=auth_session,
        db_session=session,
        entity=repository.Entities.USUARIO,
    )
    db_gastos_fixos, _, _ = await repository.get(
        auth_session=auth_session,
        db_session=session,
        entity=repository.Entities.GASTO_RECORRENTE,
    )

    import_export_entities = [
        ("insumo", "Insumos", "package_2"),
        # ("receita", "Receitas", "library_books"),
        # ("estoque", "Movimentações de Estoque", "inventory_2"),
        # ("caixa_movimentacao", "Movimentações de Caixa", "payments"),
    ]

    return await render(
        session=session,
        request=request,
        template_name="organizacao/detail.html",
        context={
            "header": context_header,
            "organizacao": db_organizacao,
            "usuarios": db_usuarios,
            "gastos_fixos": db_gastos_fixos,
            "import_export_entities": import_export_entities,
        },
    )


@router.post("/", include_in_schema=False)
async def post_organizacao_index(
    request: fastapi.Request,
    id: str = fastapi.Form(),
    descricao: str = fastapi.Form(),
    cidade: str = fastapi.Form(),
    chave_pix: str = fastapi.Form(),
    session: Session = DBSESSAO_DEP,
):
    auth_session = getattr(request.state, "auth", None)
    await repository.update(
        auth_session=auth_session,
        db_session=session,
        entity=repository.Entities.ORGANIZACAO,
        filters={"id": UUID(id)},
        values={"descricao": descricao, "cidade": cidade, "chave_pix": chave_pix},
    )
    return redirect_back(request, message="Organização atualizada com sucesso!")


@router.post("/configuracoes", include_in_schema=False)
async def post_organizacao_configuracoes(
    request: fastapi.Request,
    id: str = fastapi.Form(),
    converter_kg: bool = fastapi.Form(False),
    converter_kg_sempre: bool = fastapi.Form(False),
    usar_custo_med: bool = fastapi.Form(False),
    session: Session = DBSESSAO_DEP,
):
    auth_session = getattr(request.state, "auth", None)
    await repository.update(
        auth_session=auth_session,
        db_session=session,
        entity=repository.Entities.ORGANIZACAO,
        filters={"id": UUID(id)},
        values={
            "configuracoes": {
                "converter_kg": converter_kg,
                "converter_kg_sempre": converter_kg_sempre,
                "usar_custo_med": usar_custo_med,
            }
        },
    )
    return redirect_back(request, message="Organização atualizada com sucesso!")


@router.post("/gastos_recorrentes/criar", include_in_schema=False)
async def post_organizacao_gastos_recorrentes_criar(
    request: fastapi.Request,
    payload: inputs.GastoRecorrenteCriar = fastapi.Form(),
    session: Session = DBSESSAO_DEP,
):
    auth_session = getattr(request.state, "auth", None)
    await repository.create(
        auth_session=auth_session,
        db_session=session,
        entity=repository.Entities.GASTO_RECORRENTE,
        values={
            "organizacao_id": UUID(payload.organizacao_id),
            "descricao": payload.descricao,
            "data_inicio": payload.data_inicio,
            "valor": payload.valor,
            "tipo": payload.tipo,
            "recorrencia": payload.recorrencia,
        },
    )
    return redirect_back(request, message="Gasto Recorrente criado com sucesso!")


@router.post("/gastos_recorrentes/excluir", include_in_schema=False)
async def post_organizacao_gastos_recorrentes_excluir(
    request: fastapi.Request,
    selecionados_ids: str = fastapi.Form(),
    session: Session = DBSESSAO_DEP,
):
    auth_session = getattr(request.state, "auth", None)
    if selecionados_ids:
        for id in selecionados_ids.split(","):
            await repository.delete(
                auth_session=auth_session,
                db_session=session,
                entity=repository.Entities.GASTO_RECORRENTE,
                filters={"id": UUID(id)},
            )
    return redirect_back(request, message="Gasto Recorrente excluído com sucesso!")


@router.post("/usuarios/criar", include_in_schema=False)
async def post_organizacao_usuarios_criar(
    request: fastapi.Request,
    payload: inputs.UsuarioCriar = fastapi.Form(),
    session: Session = DBSESSAO_DEP,
):
    auth_session = getattr(request.state, "auth", None)
    if payload.senha != payload.senha_confirmar:
        return redirect_back(request, error="As senhas não batem")

    # if not payload.organizacao_id:
    #     db_organizacao = await repository.create(session, repository.Entities.ORGANIZACAO, {'descricao': payload.organizacao_descricao})
    #     payload.organizacao_id = db_organizacao.id

    await repository.create(
        auth_session=auth_session,
        db_session=session,
        entity=repository.Entities.USUARIO,
        values={
            "nome": payload.nome,
            "email": payload.email,
            "senha": payload.senha,
            "organizacao_id": payload.organizacao_id,
            "dono": payload.dono,
        },
    )
    return redirect_back(request, message="Usuário criado com sucesso!")


@router.post("/usuarios/editar", include_in_schema=False)
async def post_organizacao_usuarios_editar(
    request: fastapi.Request,
    payload: inputs.UsuarioEditar = fastapi.Form(),
    session: Session = DBSESSAO_DEP,
):
    auth_session = getattr(request.state, "auth", None)
    await repository.update(
        auth_session=auth_session,
        db_session=session,
        entity=repository.Entities.USUARIO,
        filters={"id": payload.id},
        values={
            "nome": payload.nome,
            "email": payload.email,
            "dono": payload.dono,
            "senha": payload.senha,
        },
    )
    return redirect_back(request, message="Usuário atualizado com sucesso!")


@router.post("/usuarios/excluir", include_in_schema=False)
async def post_organizacao_usuarios_excluir(
    request: fastapi.Request,
    selecionados_ids: str = fastapi.Form(),
    session: Session = DBSESSAO_DEP,
):
    auth_session = getattr(request.state, "auth", None)
    if selecionados_ids:
        for id in selecionados_ids.split(","):
            await repository.delete(
                auth_session=auth_session,
                db_session=session,
                entity=repository.Entities.USUARIO,
                filters={"id": int(id)},
            )
    return redirect_back(request, message="Usuário excluído com sucesso!")


@router.get("/sistema/recarregar", include_in_schema=False)
async def post_organizacao_sistema_recarregar(
    request: fastapi.Request, session: Session = DBSESSAO_DEP
):
    auth_session = getattr(request.state, "auth", None)
    await repository.recarregar_cache(auth_session=auth_session, db_session=session)
    return redirect_back(request, message="Sistema recarregado com sucesso!")


@router.post("/importar/{entity}", include_in_schema=False)
async def post_organizacao_importar_dados(
    request: fastapi.Request,
    arquivo_csv: fastapi.UploadFile = fastapi.Form(),
    entity: str = fastapi.Path(),
    session: Session = DBSESSAO_DEP,
):
    entity = repository.Entities[entity.upper()]
    auth_session = getattr(request.state, "auth", None)
    try:
        rows = csv_parse(file=arquivo_csv, entity=entity.value, rows_limit=100)
    except ValueError as error:
        return redirect_back(request, error=str(error))

    await repository.bulk_create(
        auth_session=auth_session,
        db_session=session,
        entity=entity,
        values=rows,
    )
    return redirect_back(request, message="Insumos importados com sucesso!")


@router.get("/exportar/{entity}", include_in_schema=False)
async def get_organizacao_exportar_dados(
    request: fastapi.Request,
    entity: str = fastapi.Path(),
    session: Session = DBSESSAO_DEP,
):
    entity = repository.Entities[entity.upper()]
    auth_session = getattr(request.state, "auth", None)

    rows, _, _ = await repository.get(
        db_session=session, entity=entity, auth_session=auth_session, per_page=99999
    )

    data = [r.data_csv() for r in rows]

    return csv_response(data=data, file_name=f"{entity.value.__name__}_dados.csv")


@router.get("/importar/{entity}/modelo", include_in_schema=False)
async def get_post_organizacao_importar_dados_modelo(
    request: fastapi.Request,
    entity: str = fastapi.Path(),
    session: Session = DBSESSAO_DEP,
):
    """Retorna um arquivo CSV com o modelo de importação de insumos"""
    entity = repository.Entities[entity.upper()]
    models = {
        repository.Entities.CAIXA_MOVIMENTACAO: [],
        repository.Entities.INSUMO: [
            {"nome": "Farinha de Trigo", "peso": 1000, "custo": 5.99, "unidade": "g"},
            {"nome": "Ovos (dúzia)", "peso": 12, "custo": 10.00, "unidade": "un"},
        ],
        repository.Entities.RECEITA: [],
        repository.Entities.RECEITA_GASTO: [],
        repository.Entities.ESTOQUE: [],
        repository.Entities.GASTO_RECORRENTE: [],
        repository.Entities.USUARIO: [],
    }
    return csv_response(
        data=models[entity], file_name=f"{entity.value.__name__}_modelo.csv"
    )
