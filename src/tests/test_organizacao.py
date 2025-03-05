import json
from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup

from src.tests.mocks import MOCK_ORGANIZACAO
from src.tests.utils import autenticar


async def __get_organizacao(test_client):
    response = await test_client.get('/app/organizacao')
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup


@pytest.mark.asyncio
async def test_get_organizacao_index(client):
    await autenticar(client)
    soup = await __get_organizacao(client)

    main_form = soup.find('form', {'id': 'form-organizacao'})
    dom_input_descricao = main_form.find('input', {'name': 'descricao'})
    dom_input_cidade = main_form.find('input', {'name': 'cidade'})
    dom_input_chave_pix = main_form.find('input', {'name': 'chave_pix'})

    assert dom_input_descricao
    assert dom_input_cidade
    assert dom_input_chave_pix

    assert dom_input_descricao.get('value') == MOCK_ORGANIZACAO.descricao
    assert dom_input_cidade.get('value') == MOCK_ORGANIZACAO.cidade
    assert dom_input_chave_pix.get('value') == MOCK_ORGANIZACAO.chave_pix


@pytest.mark.asyncio
async def test_post_organizacao_index(client):
    await autenticar(client)
    response = await client.post('/app/organizacao', data={
        'id': MOCK_ORGANIZACAO.id,
        'descricao': 'teste',
        'cidade': MOCK_ORGANIZACAO.cidade,
        'chave_pix': MOCK_ORGANIZACAO.chave_pix
    })
    assert response.status_code == 200

    soup = await __get_organizacao(client)
    main_form = soup.find('form', {'id': 'form-organizacao'})
    dom_input_descricao = main_form.find('input', {'name': 'descricao'})
    assert dom_input_descricao
    assert dom_input_descricao.get('value') == 'teste'


@pytest.mark.asyncio
async def test_post_organizacao_configuracoes(client):
    await autenticar(client)
    response = await client.post('/app/organizacao/configuracoes', data={
        'id': MOCK_ORGANIZACAO.id,
        'converter_kg': True
    })
    assert response.status_code == 200

    soup = await __get_organizacao(client)
    main_form = soup.find('form', {'id': 'form-configuracoes'})
    dom_input_descricao = main_form.find('input', {'name': 'converter_kg'})
    assert dom_input_descricao
    assert dom_input_descricao.get('checked', False) != False


@pytest.mark.asyncio
async def test_post_organizacao_usuarios_criar(client):
    await autenticar(client)
    response = await client.post('/app/organizacao/usuarios/criar', data={
        'nome': 'Outro Zé do Teste',
        'email': 'outro@email.com',
        'senha': 'teste',
        'senha_confirmar': 'teste',
        'organizacao_id': MOCK_ORGANIZACAO.id,
    })
    assert response.status_code == 200

    soup = await __get_organizacao(client)
    dom_table = soup.find('table', {'id': 'table_usuarios'})
    dom_table_trs = dom_table.find_all('tr', {'data-bs-payload': True})
    usuarios_nomes = [
        json.loads(tr.get('data-bs-payload'))['nome']
        for tr in dom_table_trs
    ]
    assert usuarios_nomes
    assert any([nome == 'Outro Zé do Teste' for nome in usuarios_nomes])


@pytest.mark.asyncio
async def test_post_organizacao_usuarios_criar_senhas_nao_batem(client):
    await autenticar(client)
    response = await client.post('/app/organizacao/usuarios/criar', data={
        'nome': 'Outro Zé do Teste',
        'email': 'outro@email.com',
        'senha': 'foo',
        'senha_confirmar': 'bar',
        'organizacao_id': MOCK_ORGANIZACAO.id,
    })
    assert response.status_code == 200
    soup = await __get_organizacao(client)
    dom_alert = soup.find('div', {'role': 'alert '})
    # breakpoint()
    # assert 'As senhas não batem' in dom_alert.text


def test_organizacao_chave_pix_valida_exception(client):
    with patch.object(MOCK_ORGANIZACAO, 'cidade', return_value=Exception('Erro teste')):
        assert MOCK_ORGANIZACAO.chave_pix_valida == False
