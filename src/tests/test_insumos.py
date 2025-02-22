import json

from bs4 import BeautifulSoup

from src.tests.utils import autenticar


def test_get_insumos_index(client, mock_repository_get):
    autenticar(client)
    response = client.get('/app/insumos', params={
        'filter_data_inicio': '2025-02-20',
        'filter_data_final': '2025-02-21'
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
