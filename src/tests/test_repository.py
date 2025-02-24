
import pytest

from src.domain import repository


def test_repository_get(mock_session):
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


def test_repository_get_order_by_first(mock_session):
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


def test_repository_update(mock_session):
    def __update(estoque_id: int):
        return repository.update(
            session=mock_session,
            entity=repository.Entities.ESTOQUE,
            filters={
                'id': estoque_id
            },
            values={
                'quantidade': 100,
                'valor_nulo': None
            }
        )
    result = __update(2)
    assert result

    with pytest.raises(ValueError):  # Registro inexistente
        __update(-1)


def test_repository_update_usuario_senha(mock_session):
    def __update_senha(usuario_id: int, senha_atual: str, senha: str):
        return repository.update(
            session=mock_session,
            entity=repository.Entities.USUARIO,
            filters={
                'id': usuario_id
            },
            values={
                'senha': senha,
                'senha_atual': senha_atual
            }
        )
    result = __update_senha(1, 'teste', 'teste')
    assert result

    with pytest.raises(ValueError):  # Senha atual incorreta
        __update_senha(1, 'foo', 'bar')

    with pytest.raises(ValueError):  # Sem permissão (outro usuário)
        __update_senha(2, 'teste', 'teste')


def test_repository_update_organizacao_sem_permissao(mock_session):
    with pytest.raises(ValueError):
        repository.update(
            session=mock_session,
            entity=repository.Entities.ORGANIZACAO,
            filters={
                'id': 1
            },
            values={
                'cidade': 'teste'
            }
        )


def test_repository_delete(mock_session):
    def __delete(id, organizacao: bool = False, usuario: bool = False):
        entity = repository.Entities.ESTOQUE
        if organizacao:
            entity = repository.Entities.ORGANIZACAO
        if usuario:
            entity = repository.Entities.USUARIO
        return repository.delete(
            session=mock_session,
            entity=entity,
            filters={
                'id': id
            }
        )
    result = __delete(1)
    assert result

    with pytest.raises(ValueError):  # Registro inexistente
        __delete(-1)

    with pytest.raises(ValueError):  # Não pode deletar organização
        __delete(1, organizacao=True)

    with pytest.raises(ValueError):  # Não pode deletar outro usuário
        __delete(2, usuario=True)


def test_repository_create(mock_session):
    result = repository.create(
        session=mock_session,
        entity=repository.Entities.RECEITA,
        values={
            'nome': 'teste'
        }
    )
    assert result
