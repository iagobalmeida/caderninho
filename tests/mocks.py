import uuid
from datetime import datetime, timedelta

from caderninho.src.domain import repository
from caderninho.src.domain.schemas import GastoRecorrencia, GastoTipo
from caderninho.src.schemas.auth import AuthSession

MOCK_ORGANIZACAO = repository.Entities.ORGANIZACAO.value(
    id=uuid.uuid4(),
    descricao="Organização Teste",
    cidade="Piracicaba",
    cnpj="123456789123",
    chave_pix="12312312323",
)

USUARIO_DONO_ID = uuid.uuid4()
MOCK_USUARIO_DONO = repository.Entities.USUARIO.value(
    id=USUARIO_DONO_ID,
    organizacao_id=MOCK_ORGANIZACAO.id,
    nome="Zé do teste (Dono)",
    email="teste@email.com",
    senha="teste",
    dono=True,
)
MOCK_USUARIO_DONO.hash_senha()

MOCK_USUARIO_ADMIN = repository.Entities.USUARIO.value(
    id=uuid.uuid4(),
    nome="Administrador",
    email="admin@email.com",
    senha="admin",
    administrador=True,
)
MOCK_USUARIO_ADMIN.hash_senha()

MOCK_USUARIO_SENHA_RECUPERADA = repository.Entities.USUARIO.value(
    id=uuid.uuid4(),
    nome="Zé do teste (Senha recuperada)",
    email="teste_2@email.com",
    senha="teste",
    administrador=True,
)
MOCK_USUARIO_ADMIN.hash_senha()

INSUMO_ID = uuid.uuid4()
MOCK_INSUMO = repository.Entities.INSUMO.value(
    id=INSUMO_ID,
    organizacao_id=MOCK_ORGANIZACAO.id,
    nome="Insumo teste",
    peso=1.0,
    custo=1.0,
)

ESTOQUE_ID = uuid.uuid4()
MOCK_ESTOQUE = repository.Entities.ESTOQUE.value(
    id=ESTOQUE_ID,
    organizacao_id=MOCK_ORGANIZACAO.id,
    descricao="Movimentação teste",
    data_criacao=datetime.now(),
    insumo_id=INSUMO_ID,
)

RECEITA_ID = uuid.uuid4()
MOCK_RECEITA = repository.Entities.RECEITA.value(
    id=RECEITA_ID,
    organizacao_id=MOCK_ORGANIZACAO.id,
    nome="Receita Teste",
    peso_unitario=100.0,
)

CAIXA_MOVIMENTACAO_ID = uuid.uuid4()
MOCK_CAIXA_MOVIMENTACAO = repository.Entities.CAIXA_MOVIMENTACAO.value(
    id=CAIXA_MOVIMENTACAO_ID,
    organizacao_id=MOCK_ORGANIZACAO.id,
    descricao="CaixaMovimentacao teste",
    valor=100.0,
)

MOCK_GASTO_RECORRENTE_SALARIO_MOTOBY = repository.Entities.GASTO_RECORRENTE.value(
    id=uuid.uuid4(),
    organizacao_id=MOCK_ORGANIZACAO.id,
    data_inicio=datetime.now() - timedelta(days=45),
    descricao="Salário Motoboy",
    valor=25.0,
    recorrencia=GastoRecorrencia.SEMANAL,
)


MOCK_GASTO_RECORRENTE_ALUGUEL = repository.Entities.GASTO_RECORRENTE.value(
    id=uuid.uuid4(),
    organizacao_id=MOCK_ORGANIZACAO.id,
    data_inicio=datetime.now() - timedelta(days=45),
    descricao="Aluguel",
    valor=100.0,
    recorrencia=GastoRecorrencia.MENSAL,
)


MOCK_GASTO_RECORRENTE_TRIBUTOS = repository.Entities.GASTO_RECORRENTE.value(
    id=uuid.uuid4(),
    organizacao_id=MOCK_ORGANIZACAO.id,
    data_inicio=datetime.now() - timedelta(days=45),
    descricao="Imposto",
    tipo=GastoTipo.PERCENTUAL,
    valor=2,
    recorrencia=GastoRecorrencia.SEMANAL,
)

MOCK_AUTH_SESSION = AuthSession(
    valid=True,
    id=MOCK_USUARIO_DONO.id,
    nome=MOCK_USUARIO_DONO.nome,
    email=MOCK_USUARIO_DONO.email,
    dono=False,
    administrador=False,
    organizacao_id=MOCK_ORGANIZACAO.id,
    organizacao_descricao=MOCK_ORGANIZACAO.descricao,
)


class MockSMTPServer:
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
        raise ValueError("Erro teste")
