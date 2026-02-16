import json

import pytest
from bs4 import BeautifulSoup

from caderninho.src.tests.mocks import INSUMO_ID, MOCK_RECEITA, RECEITA_ID
from caderninho.src.tests.utils import autenticar


async def __get_estoques_rows(test_client, filter_insumo_id=None):
    params = {
        "filter_data_inicio": "2025-01-01",
        "filter_data_final": "2025-12-01",
    }
    if filter_insumo_id:
        params.update(filter_insumo_id=filter_insumo_id)

    response = await test_client.get("/app/estoques?per_page=100", params=params)
    soup = BeautifulSoup(response.content, "html.parser")
    dom_table = soup.find("table", {"id": "table-list"})
    assert dom_table

    dom_rows = dom_table.find_all("tr")
    assert dom_rows

    dom_rows.pop(0)
    return dom_rows


@pytest.mark.asyncio
async def __assert_row_with_data_bs_payload(test_client, expected_values: dict):
    dom_rows = await __get_estoques_rows(test_client)
    dom_rows_data_bs_payload = [
        json.loads(row.get("data-bs-payload", "{}")) for row in dom_rows
    ]
    result = any(
        [
            all([row.get(key, None) == value for key, value in expected_values.items()])
            for row in dom_rows_data_bs_payload
        ]
    )
    if not result:
        breakpoint()
    assert result


@pytest.mark.asyncio
async def test_get_estoques_index(client):
    await autenticar(client)
    await __assert_row_with_data_bs_payload(client, {"descricao": "Compra"})


@pytest.mark.asyncio
async def test_post_estoque_index_uso_em_receita(client):
    await autenticar(client)
    response = await client.post(
        "/app/estoques",
        data={
            "descricao": "Uso em receita",
            "receita_id": RECEITA_ID,
            "quantidade_receita": 2,
        },
    )
    assert response.status_code == 200

    soup = BeautifulSoup(response.content, "html.parser")
    alerts = soup.find_all("div", {"role": "alert"})
    assert any(["Movimentação criada com sucesso!" in alert.text for alert in alerts])

    await __assert_row_with_data_bs_payload(
        client,
        {
            "descricao": f"Uso em Receita ({MOCK_RECEITA.nome})",
            "quantidade": -200.0,
            "insumo_id": str(INSUMO_ID),
        },
    )


@pytest.mark.asyncio
async def test_post_estoque_index_compra(client):
    await autenticar(client)
    response = await client.post(
        "/app/estoques",
        data={
            "descricao": "Compra",
            "insumo_id": INSUMO_ID,
            "quantidade_insumo": 10,
            "valor_pago": 100,
        },
    )
    assert response.status_code == 200
    await __assert_row_with_data_bs_payload(
        client,
        {
            "descricao": "Compra",
            "insumo_id": str(INSUMO_ID),
            "quantidade": 10,
            "valor_pago": 100,
        },
    )


@pytest.mark.asyncio
async def test_post_estoque_index_outros(client):
    await autenticar(client)
    response = await client.post(
        "/app/estoques",
        data={
            "descricao": "Outros",
            "descricao_customizada": "Ingrediente venceu",
            "insumo_id": INSUMO_ID,
            "quantidade_insumo": 10,
        },
    )
    assert response.status_code == 200
    await __assert_row_with_data_bs_payload(
        client,
        {
            "descricao": "Ingrediente Venceu",
            "insumo_id": str(INSUMO_ID),
            "quantidade": -10,
        },
    )
