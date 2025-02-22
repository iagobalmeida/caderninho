import json

from bs4 import BeautifulSoup

from src.tests.utils import autenticar


def test_get_vendas_index(client, mock_repository_get):
    autenticar(client)
    response = client.get('/app/organizacao')

    soup = BeautifulSoup(response.content, 'html.parser')

    dom_input_descricao = soup.find('input', {'name': 'descricao'})
    dom_input_cidade = soup.find('input', {'name': 'cidade'})
    dom_input_chave_pix = soup.find('input', {'name': 'chave_pix'})

    assert dom_input_descricao
    assert dom_input_cidade
    assert dom_input_chave_pix
