import json

from bs4 import BeautifulSoup

from src.tests.utils import autenticar


def __get_receitas_rows(test_client):
    response = test_client.get('/app/receitas', params={
        'filter_data_inicio': '2025-01-01',
        'filter_data_final': '2025-12-01'
    })

    soup = BeautifulSoup(response.content, 'html.parser')
    dom_table = soup.find('table')
    assert dom_table

    dom_rows = dom_table.find_all('tr')
    assert dom_rows

    dom_rows.pop(0)

    return dom_rows


def test_get_receitas_index(client):
    autenticar(client)
    dom_rows = __get_receitas_rows(client)

    for row in dom_rows:
        if 'Nenhum registro encontrado' in row.text:
            continue
        data_bs_payload = json.loads(row.get('data-bs-payload'))
        assert data_bs_payload.get('id', None) != None


def test_get_receita(client):
    autenticar(client)
    response = client.get('/app/receitas/1')
    soup = BeautifulSoup(response.content, 'html.parser')

    expected_inputs = ['id', 'nome', 'peso_unitario', 'porcentagem_lucro']
    for input_name in expected_inputs:
        dom_input = soup.find('input', {'name': input_name})
        assert dom_input


def test_get_receita_inexistente(client):
    autenticar(client)
    response = client.get('/app/receitas/999')
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, 'html.parser')
    # TODO: Aprimorar assert para conteúdos da tela


def test_post_receitas_index(client):
    autenticar(client)
    response = client.post('/app/receitas', data={
        'nome': 'Nova Receita Teste'
    })
    assert response.status_code == 200
    dom_rows = __get_receitas_rows(client)
    # TODO: Aprimorar assert para conteúdos da tela


def test_post_receitas_atualizar(client):
    autenticar(client)
    response = client.post('/app/receitas/atualizar', data={
        'id': 1,
        'nome': 'Receita Atualizada',
        'peso_unitario': 200,
        'porcentagem_lucro': 33,
    })
    assert response.status_code == 200
    dom_rows = __get_receitas_rows(client)
    # TODO: Aprimorar assert para conteúdos da tela


def test_post_receitas_insumos_remover(client):
    autenticar(client)
    response = client.post('/app/receitas/insumos/remover', data={
        'receita_id': 1,
        'selecionados_ids': '1'
    })
    assert response.status_code == 200
    dom_rows = __get_receitas_rows(client)
    # TODO: Aprimorar assert para conteúdos da tela


def test_post_receitas_deletar(client):
    autenticar(client)
    response = client.post('/app/receitas/deletar', data={
        'selecionados_ids': '1'
    })
    assert response.status_code == 200
    dom_rows = __get_receitas_rows(client)
    # TODO: Aprimorar assert para conteúdos da tela
