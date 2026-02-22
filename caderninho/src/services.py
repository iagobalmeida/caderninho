import json
import re
from typing import List
from uuid import UUID

import fastapi
from loguru import logger
from sqlmodel import Session

from caderninho.src.domain import repository
from caderninho.src.templates import render
from caderninho.src.templates.context import Button, Context
from caderninho.src.utils import redirect_back

ENTITY_SYMBOLS = {
    "Estoque": "inventory_2",
    "Insumo": "package_2",
    "Receita": "library_books",
    "CaixaMovimentacao": "payments",
}


async def list_entity(
    request: fastapi.Request,
    db_session: Session,
    entity: repository.Entities,
    page: int = 1,
    per_page: int = 30,
    filters: dict = {},
    table_modal: bool = True,
):
    auth_session = getattr(request.state, "auth", None)
    title_parts = re.findall(r"[A-Z][a-z]*", entity.value.__name__)
    page_title = " ".join(title_parts)
    title = "_".join([p.lower() for p in title_parts])

    order_by = None
    desc = False
    if hasattr(entity.value, "data_criacao"):
        order_by = "data_criacao"
        desc = True

    entities, pages, count = await repository.get(
        auth_session=auth_session,
        db_session=db_session,
        entity=entity,
        filters=filters,
        order_by=order_by,
        page=page,
        per_page=per_page,
        desc=desc,
    )

    table_columns = entity.value.columns()
    table_data = entities
    table_no_result = "Nenhum registro encontrado"

    delete_url = str(request.url_for(f"post_{title}_excluir"))

    logger.debug(entity.value.__name__)

    context_header = Context.Header(
        pretitle="Registros",
        title=page_title,
        symbol=ENTITY_SYMBOLS.get(entity.value.__name__, "star"),
        buttons=[
            Button(
                content="Excluír Selecionados",
                classname="btn",
                symbol="delete",
                attributes={
                    "id": "btn-excluir-selecionados",
                    "disabled": "true",
                    "data-bs-toggle": "modal",
                    "data-bs-target": "#modalConfirm",
                    "data-bs-payload": json.dumps(
                        {
                            "action": delete_url,
                            ".text-secondary": f"Excluir {page_title}(s) selecionadas?",
                        }
                    ),
                },
            ),
            Button(
                content=f"Criar {page_title}",
                classname="btn btn-success",
                symbol="add",
                attributes={
                    "data-bs-toggle": "modal",
                    "data-bs-target": f"#modalCreate{entity.value.__name__}",
                },
            ),
            Button(
                content=f"",
                classname="btn ps-2 pe-1",
                symbol="settings",
                attributes={
                    "data-bs-toggle": "modal",
                    "data-bs-target": f"#modalTablePreferences",
                    "data-bs-payload": json.dumps(
                        {
                            "#inputsWrapper": "".join(
                                [
                                    f"""<label class="form-check">
                                        <input class="form-check-input" type="checkbox" name="{c}" />
                                        <span class="form-check-label">{c.title()}</span>
                                    </label>"""
                                    for c in table_columns
                                ]
                            )
                        }
                    ),
                },
            ),
        ],
    )

    db_insumos, _, _ = await repository.get(
        auth_session=auth_session,
        db_session=db_session,
        entity=repository.Entities.INSUMO,
    )

    context = {
        "header": context_header,
        "table_columns": table_columns,
        "table_data": table_data,
        "table_no_result": table_no_result,
        "table_pages": pages,
        "table_count": count,
        "insumos": db_insumos,
        "filter_insumo_id": filters.get("insumo_id", None),
        "filter_data_inicio": filters.get("data_inicio", None),
        "filter_data_final": filters.get("data_final", None),
        "filter_pesquisa": filters.get("nome__like", None),
    }

    context.update(
        is_filtering=(
            context["filter_insumo_id"]
            or context["filter_data_inicio"]
            or context["filter_data_final"]
            or context["filter_pesquisa"]
        )
    )

    if table_modal:
        context.update(table_modal=f"#modalEdit{entity.value.__name__}")

    return await render(
        session=db_session,
        request=request,
        template_name="layout/list.html",
        context=context,
    )


async def delete_entity(
    request: fastapi.Request,
    db_session: Session,
    entity: repository.Entities,
    ids: List[UUID],
):
    auth_session = getattr(request.state, "auth", None)
    for id in ids:
        try:
            await repository.delete(
                auth_session=auth_session,
                db_session=db_session,
                entity=entity,
                filters={"id": UUID(id)},
            )
        except ValueError as ex:
            logger.error(ex)
            continue
    return redirect_back(
        request, message=f"{len(ids)} registros excluídos com sucesso!"
    )
