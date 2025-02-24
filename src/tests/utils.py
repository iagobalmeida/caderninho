from src.tests.mocks import MOCK_USUARIO_DONO


def autenticar(app_client):
    return app_client.post('/app/auth', data={
        'email': MOCK_USUARIO_DONO.email,
        'senha': MOCK_USUARIO_DONO.senha
    })
