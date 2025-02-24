import json

from bs4 import BeautifulSoup

from src.tests.utils import autenticar


def __get_receitas_rows(test_client):
    response = test_client.get('/app/vendas', params={
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


def test_get_vendas_index(client):
    autenticar(client)
    dom_rows = __get_receitas_rows(client)

    for row in dom_rows:
        if 'Nenhum registro encontrado' in row.text:
            continue
        data_bs_payload = json.loads(row.get('data-bs-payload'))
        assert data_bs_payload.get('id', None) != None


def test_post_vendas_index(client):
    autenticar(client)
    response = client.post('/app/vendas', data={
        'descricao': 'Venda teste',
        'valor': 100.00
    })
    assert response.status_code == 200
    dom_rows = __get_receitas_rows(client)
    # TODO: Aprimorar assert para conteúdos da tela


def test_post_vendas_excluir(client):
    autenticar(client)
    response = client.post('/app/vendas/excluir', data={
        'selecionados_ids': '1'
    })
    assert response.status_code == 200
    dom_rows = __get_receitas_rows(client)
    # TODO: Aprimorar assert para conteúdos da tela


def test_post_vendas_marcar_recebido(client):
    autenticar(client)
    response = client.post('/app/vendas/marcar/recebido', data={
        'selecionados_ids': '2'
    })
    assert response.status_code == 200
    dom_rows = __get_receitas_rows(client)
    # TODO: Aprimorar assert para conteúdos da tela


def test_post_vendas_marcar_pendente(client):
    autenticar(client)
    response = client.post('/app/vendas/marcar/pendente', data={
        'selecionados_ids': '2'
    })
    assert response.status_code == 200
    dom_rows = __get_receitas_rows(client)
    # TODO: Aprimorar assert para conteúdos da tela


def test_post_vendas_atualizar(client):
    autenticar(client)
    response = client.post('/app/vendas/atualizar', data={
        'id': 2,
        'descricao': 'Venda Atualizada',
        'valor': 100,
        'recebido': True
    })
    assert response.status_code == 200
    dom_rows = __get_receitas_rows(client)
    # TODO: Aprimorar assert para conteúdos da tela
