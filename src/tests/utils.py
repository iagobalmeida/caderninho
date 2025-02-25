from src.tests.mocks import MOCK_USUARIO_ADMIN, MOCK_USUARIO_DONO


def autenticar(app_client):
    return app_client.post('/app/auth', data={
        'email': MOCK_USUARIO_DONO.email,
        'senha': 'teste'
    })


def autenticar_admin(app_client):
    return app_client.post('/app/auth', data={
        'email': MOCK_USUARIO_ADMIN.email,
        'senha': 'admin'
    })
