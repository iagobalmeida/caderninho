from bs4 import BeautifulSoup


def test_post_index(client, mock_repository_get):
    response = client.post('/app/auth', data={
        'email': 'teste@email.com',
        'senha': 'teste'
    })
    assert b'Home' in response.content


def test_post_index_senha_incorreta(client, mock_repository_get):
    response = client.post('/app/auth', data={
        'email': 'teste@email.com',
        'senha': 'senha_incorreta'
    })
    soup = BeautifulSoup(response.content, 'html.parser')
    dom_error = soup.find('h4', 'text-danger')
    assert dom_error and '401' in dom_error.text
