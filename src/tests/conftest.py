from datetime import datetime
from unittest.mock import MagicMock, patch

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

MOCK_USUARIO_DONO = repository.Entities.USUARIO.value(
    id=1,
    organizacao_id=MOCK_ORGANIZACAO.id,
    nome='Zé do teste (Dono)',
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

MOCK_VENDA = repository.Entities.VENDA.value(
    id=1,
    organizacao_id=MOCK_ORGANIZACAO.id,
    descricao='Venda teste',
    valor=100.0
)


def __mock_repository_get_side_effect(*args, **kwargs):
    ret = None
    first = kwargs.get('first', False)
    entity = kwargs.get('entity', None)

    if entity == repository.Entities.USUARIO:
        ret = [MOCK_USUARIO_DONO]
    if entity == repository.Entities.ESTOQUE:
        ret = [MOCK_ESTOQUE]
    if entity == repository.Entities.RECEITA:
        ret = [MOCK_RECEITA]
    if entity == repository.Entities.ORGANIZACAO:
        ret = [MOCK_ORGANIZACAO]
    if entity == repository.Entities.VENDA:
        ret = [MOCK_VENDA]

    id = kwargs.get('filters', {}).get('id', None)
    if id and ret:
        ret[0].id = id

        if id == -1:
            ret = None

    return (ret[0] if ret and first else ret), None, None


@pytest.fixture
def mock_repository_get():
    with patch.object(repository, 'get') as patch_repo_get:
        patch_repo_get.side_effect = __mock_repository_get_side_effect
        yield


@pytest.fixture
def mock_session():
    """Cria um mock da sessão autenticada"""
    session = MagicMock()
    session.exec.return_value.all.return_value = ["item1", "item2"]
    session.exec.return_value.first.return_value = "item1"
    session.exec.return_value.one.return_value = 2
    session.sessao_autenticada = MagicMock()
    session.sessao_autenticada.administrador = False
    session.sessao_autenticada.dono = False
    session.sessao_autenticada.organizacao_id = 1
    session.sessao_autenticada.id = 1
    return session


@pytest.fixture
def client():
    test_client = TestClient(app)
    yield test_client
