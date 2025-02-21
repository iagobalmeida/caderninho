from math import ceil
from unittest.mock import MagicMock

import pytest

from src.domain import repository


@pytest.fixture
def mock_session():
    """Cria um mock da sessão autenticada"""
    session = MagicMock()
    session.exec.return_value.all.return_value = ["item1", "item2"]
    session.exec.return_value.first.return_value = "item1"
    session.exec.return_value.one.return_value = 2  # Simula count = 2
    session.sessao_autenticada = MagicMock()
    session.sessao_autenticada.administrador = False
    session.sessao_autenticada.organizacao_id = 1
    return session


def test_get(mock_session):
    result = repository.get(
        session=mock_session,
        entity=repository.Entities.ESTOQUE,
        filters={
            'filtro_sem_valor': None,
            'data_inicio': '2025-01-01',
            'data_final': '2025-02-01',
            'insumo_id': 1
        },
        order_by='id',
        desc=True
    )
    assert result


def test_get_order_by_first(mock_session):
    result = repository.get(
        session=mock_session,
        entity=repository.Entities.ESTOQUE,
        filters={
            'filtro_sem_valor': None,
            'data_inicio': '2025-01-01',
            'data_final': '2025-02-01',
        },
        order_by='id',
        first=True
    )
    assert result
