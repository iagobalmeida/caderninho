import json

from bs4 import BeautifulSoup

from src.tests.utils import autenticar


def __get_insumos_rows(test_client):
    response = test_client.get('/app/insumos', params={
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


def test_get_insumos_index(client):
    autenticar(client)
    dom_rows = __get_insumos_rows(client)

    for row in dom_rows:
        if 'Nenhum registro encontrado' in row.text:
            continue
        data_bs_payload = json.loads(row.get('data-bs-payload'))
        assert data_bs_payload.get('id', None) != None


def test_post_insumos_index(client):
    autenticar(client)
    response = client.post('/app/insumos', data={
        'nome': 'Ingrediente Teste',
        'peso': 200,
        'custo': 5,
        'unidade': 'g'
    })
    assert response.status_code == 200
    dom_rows = __get_insumos_rows(client)
    # TODO: Aprimorar assert para conteúdos da tela


def test_post_insumos_atualizar(client):
    autenticar(client)
    response = client.post('/app/insumos/atualizar', data={
        'id': 1,
        'nome': 'Ingrediente Atualizado',
        'peso': 100,
        'custo': 20,
        'unidade': 'g'
    })
    assert response.status_code == 200
    dom_rows = __get_insumos_rows(client)
    # TODO: Aprimorar assert para conteúdos da tela


def test_post_insumos_excluir(client):
    autenticar(client)
    response = client.post('/app/insumos/excluir', data={
        'selecionados_ids': '1,999'
    })
    assert response.status_code == 200
    dom_rows = __get_insumos_rows(client)
    # TODO: Aprimorar assert para conteúdos da tela
