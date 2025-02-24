from datetime import datetime

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

MOCK_USUARIO_ADMIN = repository.Entities.USUARIO.value(
    id=2,
    nome='Administrador',
    email='admin@email.com',
    senha='admin',
    administrador=True
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


def repository_get_side_effect(*args, **kwargs):
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


class MockSMTPServer():
    def __enter__(self, *args, **kwargs):
        return self  # Retorna a própria instância para ser usada no with

    def __exit__(self, *args, **kwargs):
        pass  # Nada a fazer ao sair do contexto

    def login(self, *args, **kwargs):
        return True

    def sendmail(self, *args, **kwargs):
        return True


class MockSMTPServerException(MockSMTPServer):
    def login(self, *args, **kwargs):
        raise ValueError('Erro teste')
