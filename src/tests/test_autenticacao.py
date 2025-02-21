from unittest.mock import patch

from src.domain import repository


def test_autenticacao(client):
    with patch.object(repository, 'get') as patch_repo_get:
        patch_repo_get.return_value = (repository.Entities.USUARIO.value(
            id=1,
            nome='Zé do teste',
            email='teste@email.com',
            senha='teste',
            organizacao_id=1
        ), None, None)
        response = client.post('/app/auth', data={
            'email': 'teste@email.com',
            'senha': 'teste',
            'lembrar_de_mim': True
        })
        assert b'Home' in response.content
