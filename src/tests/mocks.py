from datetime import datetime, timedelta

from src.domain import repository
from src.domain.schemas import GastoRecorrencia, GastoTipo

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
MOCK_USUARIO_DONO.hash_senha()

MOCK_USUARIO_ADMIN = repository.Entities.USUARIO.value(
    id=2,
    nome='Administrador',
    email='admin@email.com',
    senha='admin',
    administrador=True
)
MOCK_USUARIO_ADMIN.hash_senha()

MOCK_USUARIO_SENHA_RECUPERADA = repository.Entities.USUARIO.value(
    id=3,
    nome='Zé do teste (Senha recuperada)',
    email='teste_2@email.com',
    senha='teste',
    administrador=True
)
MOCK_USUARIO_ADMIN.hash_senha()

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

MOCK_CAIXA_MOVIMENTACAO = repository.Entities.CAIXA_MOVIMENTACAO.value(
    id=1,
    organizacao_id=MOCK_ORGANIZACAO.id,
    descricao='CaixaMovimentacao teste',
    valor=100.0
)

MOCK_GASTO_RECORRENTE_SALARIO_MOTOBY = repository.Entities.GASTO_RECORRENTE.value(
    id=1,
    organizacao_id=MOCK_ORGANIZACAO.id,
    data_inicio=datetime.now()-timedelta(days=45),
    descricao='Salário Motoboy',
    valor=25.0,
    recorrencia=GastoRecorrencia.SEMANAL
)


MOCK_GASTO_RECORRENTE_ALUGUEL = repository.Entities.GASTO_RECORRENTE.value(
    id=2,
    organizacao_id=MOCK_ORGANIZACAO.id,
    data_inicio=datetime.now()-timedelta(days=45),
    descricao='Aluguel',
    valor=100.0,
    recorrencia=GastoRecorrencia.MENSAL
)


MOCK_GASTO_RECORRENTE_TRIBUTOS = repository.Entities.GASTO_RECORRENTE.value(
    id=2,
    organizacao_id=MOCK_ORGANIZACAO.id,
    data_inicio=datetime.now()-timedelta(days=45),
    descricao='Imposto',
    tipo=GastoTipo.PERCENTUAL,
    valor=2,
    recorrencia=GastoRecorrencia.SEMANAL
)


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
