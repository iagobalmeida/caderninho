import re
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class PlanoBeneficio(BaseModel):
    conteudo: str
    classname: Optional[str] = None

    def __str__(self):
        conteudo = re.sub(
            r"\b\d{1,3}(?:\.\d{3})*\b", lambda m: f"<b>{m.group()}</b>", self.conteudo
        )
        attrs = ""
        classnames = ""
        if self.classname:
            attrs = 'style="--tblr-bg-opacity: .02;"'
            classnames = f"bg-{self.classname} text-{self.classname}"
        return f'<li class="list-group-item {classnames}" {attrs}>{conteudo}</li>'


class Plano(BaseModel):
    nome: str
    symbol: Optional[str] = "star"
    valor: Optional[float] = 0
    app_descricao: Optional[str] = None
    card_exibir: Optional[bool] = True
    card_descricao: Optional[str] = None
    card_beneficios: List[PlanoBeneficio] = []
    assinatura_exibir: Optional[bool] = True
    assinatura_descricao: Optional[str] = None


PLANOS_DATA = {
    "Bloqueado": Plano(
        nome="Bloqueado",
        app_descricao="Seu plano está bloqueado até que um próximo pagamento seja realizado.",
        assinatura_exibir=False,
        card_exibir=False,
    ),
    "Teste": Plano(
        nome="Teste por 7 dias",
        card_descricao="Você tera 7 dias para testar o KDerninho.",
        app_descricao="Sua conta está em período de teste gratuito.",
        assinatura_descricao="Grátis por <b>7 dias</b>",
        card_exibir=False,
    ),
    "Pequeno": Plano(
        nome="Pequeno",
        symbol="person",
        card_descricao="Para quem está começando do zero.",
        app_descricao="Seu plano atual é o <b>Pequeno</b>.",
        valor=12,
        card_beneficios=[
            PlanoBeneficio(conteudo="1 conta de Dono"),
            PlanoBeneficio(conteudo="Nenhuma Conta de Usuário", classname="danger"),
            PlanoBeneficio(conteudo="5 Receitas"),
            PlanoBeneficio(conteudo="40 Insumos"),
            PlanoBeneficio(conteudo="Até 2.000 Movimentações/mês"),
            PlanoBeneficio(conteudo="Sem exportação", classname="danger"),
        ],
    ),
    "Intermediário": Plano(
        nome="Intermediário",
        symbol="group",
        card_descricao="Para quem já tem um negócio.",
        app_descricao="Seu plano atual é o <b>Intermediário</b>.",
        valor=25,
        card_beneficios=[
            PlanoBeneficio(conteudo="2 conta de Dono", classname="primary"),
            PlanoBeneficio(conteudo="5 contas de Funcionário", classname="primary"),
            PlanoBeneficio(conteudo="50 Receitas"),
            PlanoBeneficio(conteudo="400 Insumos"),
            PlanoBeneficio(conteudo="Até 40.000 Movimentações/mês"),
            PlanoBeneficio(
                conteudo="Exportação de Caixa e Estoque", classname="primary"
            ),
        ],
    ),
    "Avançado": Plano(
        nome="Avançado",
        symbol="groups",
        card_descricao="Para largar de vez as tabelas.",
        app_descricao="Seu plano atual é o <b>Avançado</b>.",
        valor=55,
        card_beneficios=[
            PlanoBeneficio(conteudo="5 conta de Dono", classname="success"),
            PlanoBeneficio(conteudo="10 contas de Funcionário", classname="success"),
            PlanoBeneficio(conteudo="Receitas Ilimitadas", classname="success"),
            PlanoBeneficio(conteudo="Insumos Ilimitados", classname="success"),
            PlanoBeneficio(conteudo="Até 40.000 Movimentações/mês"),
            PlanoBeneficio(
                conteudo="Exportação de Caixa e Estoque", classname="success"
            ),
        ],
    ),
}


class Planos(Enum):
    BLOQUEADO = "Bloqueado"
    TESTE = "Teste"
    PEQUENO = "Pequeno"
    INTERMEDIARIO = "Intermediário"
    AVANCADO = "Avançado"


class GastoTipo(Enum):
    PERCENTUAL = "Percentual"
    FIXO = "Fixo"
    POR_UNIDADE = "Por Unidade"


class CaixMovimentacaoTipo(Enum):
    ENTRADA = "Entrada"
    SAIDA = "Saida"


class GastoRecorrencia(Enum):
    MENSAL = "Mensal"
    SEMANAL = "Semanal"
