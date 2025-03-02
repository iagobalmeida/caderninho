import json
from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup

from src.tests.mocks import MOCK_CAIXA_MOVIMENTACAO
from src.tests.utils import autenticar


async def __get_receitas_rows(test_client):
    response = await test_client.get('/app/caixa_movimentacoes', params={
        'filter_data_inicio': '2025-01-01',
        'filter_data_final': '2025-12-01'
    })
    soup = BeautifulSoup(response.content, 'html.parser')
    dom_table = soup.find('table', {'id': 'table-list'})
    assert dom_table

    dom_rows = dom_table.find_all('tr')
    assert dom_rows

    dom_rows.pop(0)
    return dom_rows


@pytest.mark.asyncio
async def test_get_caixa_movimentacoes_index(client):
    await autenticar(client)
    dom_rows = await __get_receitas_rows(client)

    for row in dom_rows:
        if 'Nenhum registro encontrado' in row.text:
            continue
        data_bs_payload = json.loads(row.get('data-bs-payload'))
        assert data_bs_payload.get('id', None) != None


@pytest.mark.asyncio
async def test_post_caixa_movimentacoes_index(client):
    await autenticar(client)
    response = await client.post('/app/caixa_movimentacoes', data={
        'descricao': 'CaixaMovimentacao teste',
        'valor': 100.00
    })
    assert response.status_code == 200
    dom_rows = await __get_receitas_rows(client)
    # TODO: Aprimorar assert para conteúdos da tela


@pytest.mark.asyncio
async def test_post_caixa_movimentacoes_excluir(client):
    await autenticar(client)
    response = await client.post('/app/caixa_movimentacoes/excluir', data={
        'selecionados_ids': '1'
    })
    assert response.status_code == 200
    dom_rows = await __get_receitas_rows(client)
    # TODO: Aprimorar assert para conteúdos da tela


@pytest.mark.asyncio
async def test_post_caixa_movimentacoes_marcar_recebido(client):
    await autenticar(client)
    response = await client.post('/app/caixa_movimentacoes/marcar/recebido', data={
        'selecionados_ids': '2'
    })
    assert response.status_code == 200
    dom_rows = await __get_receitas_rows(client)
    # TODO: Aprimorar assert para conteúdos da tela


@pytest.mark.asyncio
async def test_post_caixa_movimentacoes_marcar_pendente(client):
    await autenticar(client)
    response = await client.post('/app/caixa_movimentacoes/marcar/pendente', data={
        'selecionados_ids': '2'
    })
    assert response.status_code == 200
    dom_rows = await __get_receitas_rows(client)
    # TODO: Aprimorar assert para conteúdos da tela


@pytest.mark.asyncio
async def test_post_caixa_movimentacoes_atualizar(client):
    await autenticar(client)
    response = await client.post('/app/caixa_movimentacoes/atualizar', data={
        'id': 2,
        'descricao': 'CaixaMovimentacao Atualizada',
        'valor': 100,
        'recebido': True
    })
    assert response.status_code == 200
    dom_rows = await __get_receitas_rows(client)
    # TODO: Aprimorar assert para conteúdos da tela


@pytest.mark.asyncio
async def test_organizacao_chave_pix_valida_exception(client):
    with patch.object(MOCK_CAIXA_MOVIMENTACAO, 'valor', return_value=Exception('Erro teste')):
        assert MOCK_CAIXA_MOVIMENTACAO.gerar_qr_code('foo', 'bar', 'far') == None
