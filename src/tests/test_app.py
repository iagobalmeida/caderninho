import smtplib
from unittest.mock import patch

from bs4 import BeautifulSoup

from src.tests.mocks import MockSMTPServer


def test_get_index(client):
    response = client.get('/')
    assert response.status_code == 200


def test_get_app_index(client):
    response = client.get('/app')
    assert response.status_code == 200


def test_get_registrar(client):
    response = client.get('/app/registrar')
    assert response.status_code == 200


def test_post_registrar(client):
    response = client.post('/app/registrar', data={
        'nome': 'Novo Usuário Teste',
        'email': 'teste_app@teste.com',
        'senha': 'novo',
        'senha_confirmar': 'novo',
        'organizacao_descricao': 'Nova Organização Teste',
        'dono': True,
    })

    assert response.status_code == 200
    soup = BeautifulSoup(response.content, 'html.parser')
    alert = soup.find('h4', {'role': 'alert'})
    assert 'Conta criada com sucesso' in alert.text


def test_post_registrar_senhas_nao_batem(client):
    response = client.post('/app/registrar', data={
        'nome': 'Novo Usuário Teste',
        'email': 'teste_app@teste.com',
        'senha': 'novo',
        'senha_confirmar': 'senha_incorreta',
        'organizacao_descricao': 'Nova Organização Teste',
        'dono': True,
    })

    assert response.status_code == 200
    soup = BeautifulSoup(response.content, 'html.parser')
    alert = soup.find('h4', {'role': 'alert'})
    assert 'As senhas não batem' in alert.text


def test_app_get_recuperar_senha(client):
    response = client.get('/app/recuperar_senha')
    assert response.status_code == 200


def test_app_post_recuperar_senha_usuario_inexistente(client):
    with patch.object(smtplib, 'SMTP_SSL', return_value=MockSMTPServer()):
        response = client.post('/app/recuperar_senha', data={
            'email': 'usuario_nao_existente@teste.com',
        })
        assert response.status_code == 200
        soup = BeautifulSoup(response.content, 'html.parser')
        alert = soup.find('h4', {'role': 'alert'})
        assert 'Não foi encontrado usuário com esse email' in alert.text


def test_app_post_recuperar_senha(client):
    with patch.object(smtplib, 'SMTP_SSL', return_value=MockSMTPServer()):
        response = client.post('/app/recuperar_senha', data={
            'email': 'teste_app@teste.com',
        })
        assert response.status_code == 200
        soup = BeautifulSoup(response.content, 'html.parser')
        alert = soup.find('h4', {'role': 'alert'})
        assert 'Senha enviada para: teste_app@teste.com' in alert.text
