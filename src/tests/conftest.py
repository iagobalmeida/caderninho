from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from schemas.auth import SessaoAutenticada
from src import db
from src.app import app
from src.domain import repository

MOCK_ORGANIZACAO = repository.Entities.ORGANIZACAO.value(
    id=1,
    descricao='Organização Teste',
    cidade='Piracicaba',
    chave_pix='12312312323'
)

MOCK_USUARIO = repository.Entities.USUARIO.value(
    id=1,
    organizacao_id=MOCK_ORGANIZACAO.id,
    nome='Zé do teste',
    email='teste@email.com',
    senha='teste',
    dono=True
)

MOCK_ESTOQUE = repository.Entities.ESTOQUE.value(
    id=1,
    organizacao_id=MOCK_ORGANIZACAO.id,
    descricao='Movimentação teste',
    data_criacao=datetime.now(),
    insumo_id=1
)

MOCK_RECEITA = repository.Entities.RECEITA.value(
    id=1,
    organizacao_id=MOCK_ORGANIZACAO.id,
    nome='Receita Teste',
    peso_unitario=100.0,
)

MOCK_SESSAO_AUTENTICADA = SessaoAutenticada(
    valid=True,
    id=MOCK_USUARIO.id,
    nome=MOCK_USUARIO.nome,
    email=MOCK_USUARIO.email,
    dono=MOCK_USUARIO.dono,
    administrador=MOCK_USUARIO.administrador,
    organizacao_id=MOCK_USUARIO.organizacao_id,
    organizacao_descricao='Organização Teste'
)


def __mock_repository_get_side_effect(session, entity, fisrt: bool = False, *args, **kwargs):
    ret = None
    if entity == repository.Entities.USUARIO:
        ret = [MOCK_USUARIO]
    if entity == repository.Entities.ESTOQUE:
        ret = [MOCK_ESTOQUE]
    if entity == repository.Entities.RECEITA:
        ret = [MOCK_RECEITA]
    if entity == repository.Entities.ORGANIZACAO:
        ret = [MOCK_ORGANIZACAO]
    return (ret[0] if fisrt else ret), None, None


@pytest.fixture
def mock_repository_get():
    with patch.object(repository, 'get') as patch_repo_get:
        patch_repo_get.side_effect = __mock_repository_get_side_effect
        yield


@pytest.fixture
def client():
    test_client = TestClient(app)
    yield test_client
