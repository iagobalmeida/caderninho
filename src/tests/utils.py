from src.tests.mocks import MOCK_USUARIO_ADMIN, MOCK_USUARIO_DONO


async def autenticar(app_client):
    return await app_client.post('/app/auth', data={
        'email': MOCK_USUARIO_DONO.email,
        'senha': 'teste'
    })


async def autenticar_admin(app_client):
    result = await app_client.post('/app/auth', data={
        'email': MOCK_USUARIO_ADMIN.email,
        'senha': 'admin'
    })
    return result
