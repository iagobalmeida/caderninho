# from datetime import datetime, timedelta
# from uuid import UUID, uuid4

# import pytest

# from domain import repository
# from tests.mocks import (ESTOQUE_ID, INSUMO_ID, MOCK_AUTH_SESSION,
#                          USUARIO_DONO_ID)

# ESTOQUE_ID = uuid4()


# @pytest.mark.asyncio
# async def test_repository_create(db_session):
#     result = await repository.create(
#         db_session,
#         repository.Entities.ESTOQUE,
#         auth_session=MOCK_AUTH_SESSION,
#         values={
#             'id': ESTOQUE_ID,
#             'descricao': 'Estoque teste repositório',
#             'insumo_id': INSUMO_ID,
#             'quantidade': 10,
#             'valor_pago': 10
#         }
#     )
#     assert result  # TODO: Melhorar esse assert


# @pytest.mark.asyncio
# async def test_repository_get(db_session):
#     result, _, _ = await repository.get(
#         db_session,
#         repository.Entities.ESTOQUE,
#         auth_session=MOCK_AUTH_SESSION
#     )
#     assert all([isinstance(r.id, UUID) for r in result])  # TODO: Melhorar esse assert

#     result, _, _ = await repository.get(
#         db_session,
#         repository.Entities.ESTOQUE,
#         auth_session=MOCK_AUTH_SESSION,
#         order_by='id',
#         first=True
#     )
#     assert result.id == ESTOQUE_ID  # TODO: Melhorar esse assert


# @pytest.mark.asyncio
# async def test_repository_update(db_session):
#     result = await repository.update(
#         db_session,
#         repository.Entities.ESTOQUE,
#         auth_session=MOCK_AUTH_SESSION,
#         filters={
#             'id': ESTOQUE_ID,
#         },
#         values={
#             'quantidade': 100
#         }
#     )
#     assert result  # TODO: Melhorar esse assert


# @pytest.mark.asyncio
# async def test_repository_update_usuario_senha(db_session):
#     result = await repository.update(
#         db_session,
#         repository.Entities.USUARIO,
#         auth_session=MOCK_AUTH_SESSION,
#         filters={
#             'id': USUARIO_DONO_ID,
#         },
#         values={
#             'senha': 'teste',
#             'senha_atual': 'teste'
#         }
#     )
#     assert result  # TODO: Melhorar esse assert


# @pytest.mark.asyncio
# async def test_repository_update_usuario_senha_invalida(db_session):
#     with pytest.raises(ValueError):
#         await repository.update(
#             db_session,
#             repository.Entities.USUARIO,
#             auth_session=MOCK_AUTH_SESSION,
#             filters={
#                 'id': uuid4(),
#             },
#             values={
#                 'senha': 'teste',
#                 'senha_atual': 'senha_incorreta'
#             }
#         )


# @pytest.mark.asyncio
# async def test_repository_update_usuario_diferente(db_session):
#     with pytest.raises(ValueError):
#         await repository.update(
#             db_session,
#             repository.Entities.USUARIO,
#             auth_session=MOCK_AUTH_SESSION,
#             filters={
#                 'id': uuid4(),
#             },
#             values={
#                 'nome': 'teste'
#             }
#         )


# @pytest.mark.asyncio
# async def test_repository_update_organizacao_sem_ser_dono(db_session):
#     with pytest.raises(ValueError):
#         await repository.update(
#             db_session,
#             repository.Entities.ORGANIZACAO,
#             auth_session=MOCK_AUTH_SESSION,
#             filters={
#                 'id': uuid4(),
#             },
#             values={
#                 'chave_pix': 'chave_pix_aleatoria'
#             }
#         )


# @pytest.mark.asyncio
# async def test_repository_update_registro_nao_encontrado(db_session):
#     with pytest.raises(ValueError):
#         await repository.update(
#             db_session,
#             repository.Entities.ESTOQUE,
#             auth_session=MOCK_AUTH_SESSION,
#             filters={
#                 'id': uuid4(),
#             },
#             values={
#                 'quantidade': 100
#             }
#         )


# @pytest.mark.asyncio
# async def test_repository_delete(db_session):
#     result = await repository.delete(
#         db_session,
#         repository.Entities.ESTOQUE,
#         auth_session=MOCK_AUTH_SESSION,
#         filters={
#             'id': ESTOQUE_ID
#         }
#     )
#     assert result  # TODO: Melhorar esse assert


# @pytest.mark.asyncio
# async def test_repository_delete_organizacao(db_session):
#     with pytest.raises(ValueError):
#         await repository.delete(
#             db_session,
#             repository.Entities.ORGANIZACAO,
#             auth_session=MOCK_AUTH_SESSION,
#             filters={
#                 'id': ESTOQUE_ID
#             }
#         )


# @pytest.mark.asyncio
# async def test_repository_delete_registro_nao_encontrado(db_session):
#     with pytest.raises(ValueError):
#         await repository.delete(
#             db_session,
#             repository.Entities.ESTOQUE,
#             auth_session=MOCK_AUTH_SESSION,
#             filters={
#                 'id': str(uuid4())
#             }
#         )


# @pytest.mark.asyncio
# async def test_repository_delete_usuario_diferente(db_session):
#     with pytest.raises(ValueError):
#         await repository.delete(
#             db_session,
#             repository.Entities.USUARIO,
#             auth_session=MOCK_AUTH_SESSION,
#             filters={
#                 'id': str(uuid4())
#             }
#         )


# @pytest.mark.asyncio
# async def test_repository_get_chart_fluxo_caixa_datasets(db_session):
#     result = await repository.get_chart_fluxo_caixa_datasets(
#         auth_session=MOCK_AUTH_SESSION,
#         db_session=db_session,
#         data_inicial=datetime.now()-timedelta(days=45),
#         data_final=datetime.now()+timedelta(days=45)
#     )
#     assert result  # TODO: Melhorar esse assert
