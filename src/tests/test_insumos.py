import json

import pytest
from bs4 import BeautifulSoup

from tests.mocks import INSUMO_ID
from tests.utils import autenticar


async def __get_insumos_rows(test_client):
    response = await test_client.get('/app/insumos', params={
        'filter_data_inicio': '2025-01-01',
        'filter_data_final': '2025-12-01',
    })
    soup = BeautifulSoup(response.content, 'html.parser')
    dom_table = soup.find('table', {'id': 'table-list'})
    assert dom_table

    dom_rows = dom_table.find_all('tr')
    assert dom_rows

    dom_rows.pop(0)
    return dom_rows


@pytest.mark.asyncio
async def test_get_insumos_index(client):
    await autenticar(client)
    dom_rows = await __get_insumos_rows(client)

    for row in dom_rows:
        if 'Nenhum registro encontrado' in row.text:
            continue
        data_bs_payload = json.loads(row.get('data-bs-payload'))
        assert data_bs_payload.get('id', None) != None


@pytest.mark.asyncio
async def test_post_insumos_index(client):
    await autenticar(client)
    response = await client.post('/app/insumos', data={
        'nome': 'Ingrediente Teste',
        'peso': 200,
        'custo': 5,
        'unidade': 'g'
    })
    assert response.status_code == 200
    dom_rows = await __get_insumos_rows(client)
    # TODO: Aprimorar assert para conteúdos da tela


@pytest.mark.asyncio
async def test_post_insumos_atualizar(client):
    await autenticar(client)
    response = await client.post('/app/insumos/atualizar', data={
        'id': 1,
        'nome': 'Ingrediente Atualizado',
        'peso': 100,
        'custo': 20,
        'unidade': 'g'
    })
    assert response.status_code == 200
    dom_rows = await __get_insumos_rows(client)
    # TODO: Aprimorar assert para conteúdos da tela


@pytest.mark.asyncio
async def test_post_insumos_excluir(client):
    await autenticar(client)
    response = await client.post('/app/insumos/excluir', data={
        'selecionados_ids': f'{INSUMO_ID}'
    })
    assert response.status_code == 200
    dom_rows = await __get_insumos_rows(client)
    # TODO: Aprimorar assert para conteúdos da tela
