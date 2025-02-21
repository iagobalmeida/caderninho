import json

from bs4 import BeautifulSoup


def __autenticar(app_client):
    return app_client.post('/app/auth', data={
        'email': 'teste@email.com',
        'senha': 'teste'
    })


def test_get_estoques_index(client, mock_repository_get):
    __autenticar(client)
    response = client.get('/app/estoques', params={
        'filter_data_inicio': '2025-02-20',
        'filter_data_final': '2025-02-21',
        'filter_insumo_id': 1
    })

    soup = BeautifulSoup(response.content, 'html.parser')
    dom_table = soup.find('table')
    assert dom_table

    dom_rows = dom_table.find_all('tr')
    assert dom_rows

    dom_rows.pop(0)

    for row in dom_rows:
        if 'Nenhum registro encontrado' in row.text:
            continue
        data_bs_payload = json.loads(row.get('data-bs-payload'))
        assert data_bs_payload.get('id', None) != None

    assert b'Home' in response.content
