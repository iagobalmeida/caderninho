
def autenticar(app_client):
    return app_client.post('/app/auth', data={
        'email': 'teste@email.com',
        'senha': 'teste'
    })
