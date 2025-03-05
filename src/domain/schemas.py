from enum import Enum


class Plano(Enum):
    BLOQUEADO = 'Bloqueado'
    TESTE = 'Teste'
    PEQUENO = 'Pequeno'
    INTERMEDIARIO = 'Intermediário'
    AVANCADO = 'Avançado'


class GastoTipo(Enum):
    PERCENTUAL = 'Percentual'
    FIXO = 'Fixo'


class CaixMovimentacaoTipo(Enum):
    ENTRADA = 'Entrada'
    SAIDA = 'Saida'
