from bs4 import BeautifulSoup

from src.tests.utils import autenticar


def test_post_index(client):
    response = client.post('/app/auth', data={
        'email': 'teste@email.com',
        'senha': 'teste'
    })
    soup = BeautifulSoup(response.content, 'html.parser')
    assert b'Home' in response.content


def test_post_index_senha_incorreta(client):
    response = client.post('/app/auth', data={
        'email': 'teste@email.com',
        'senha': 'senha_incorreta'
    })
    soup = BeautifulSoup(response.content, 'html.parser')
    dom_error = soup.find('h4', 'text-danger')
    assert dom_error and '401' in dom_error.text


def test_post_index_usuario_inexistente(client):
    response = client.post('/app/auth', data={
        'email': 'nao_existo@email.com',
        'senha': 'senha_incorreta'
    })
    soup = BeautifulSoup(response.content, 'html.parser')
    dom_error = soup.find('h4', 'text-danger')
    assert dom_error and '401' in dom_error.text


def test_post_authenticate(client):
    response = client.post('/app/auth/authenticate', data={
        'email': 'teste@email.com',
        'senha': 'teste'
    })
    assert response.status_code == 200
    assert response.content == b'true'


def test_post_perfil(client):
    autenticar(client)
    response = client.post('/app/auth/perfil', data={
        'id': 1,
        'nome': 'Usuário Atualizado',
        'email': 'teste@email.com',
        'dono': True,
    })
    soup = BeautifulSoup(response.content, 'html.parser')
    dom_alert = soup.find('div', {'role': 'alert'})
    assert dom_alert and 'Perfil atualizado com sucesso!' in dom_alert.text


def test_post_atualizar_senha(client):
    autenticar(client)
    response = client.post('/app/auth/atualizar_senha', data={
        'id': 1,
        'senha_atual': 'teste',
        'senha': 'teste',
        'senha_confirmar': 'teste',
    })
    soup = BeautifulSoup(response.content, 'html.parser')
    dom_alert = soup.find('div', {'role': 'alert'})
    assert dom_alert and 'Senha alterada com sucesso!' in dom_alert.text


def test_post_atualizar_senha_senhas_nao_batem(client):
    autenticar(client)
    response = client.post('/app/auth/atualizar_senha', data={
        'id': 1,
        'senha_atual': 'teste',
        'senha': 'foo',
        'senha_confirmar': 'bar',
    })
    soup = BeautifulSoup(response.content, 'html.parser')
    dom_alert = soup.find('h4', {'role': 'alert'})
    assert dom_alert and 'As senhas não batem' in dom_alert.text


def test_post_logout(client):
    autenticar(client)
    response = client.get('/app/auth/logout')
    assert response.status_code == 200
