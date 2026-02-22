import math
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from loguru import logger
from passlib.context import CryptContext
from pixqrcode import PixQrCode
from sqlalchemy.orm import validates
from sqlmodel import JSON, Column, Field, Index, Relationship, SQLModel

from caderninho.src.domain.schemas import (
    PLANOS_DATA,
    CaixMovimentacaoTipo,
    GastoRecorrencia,
    GastoTipo,
    Planos,
)
from caderninho.src.templates import filters

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

STRFTIME_FORMAT = "%Y-%m-%d %H:%M:%S"

CSV_EXCLUDE_KEYS = ["id", "organizacao_id", "data_criacao", "data_bs_payload"]


class Organizacao(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    # Dados
    descricao: str
    cnpj: Optional[str] = None
    cidade: Optional[str] = None
    chave_pix: Optional[str] = None
    usuarios: List["Usuario"] = Relationship(back_populates="organizacao")
    # Plano & pagamento
    plano: Optional[Planos] = Planos.TESTE
    plano_expiracao: Optional[datetime] = Field(
        default=datetime.now() + timedelta(days=7), nullable=False
    )
    gastos_recorrentes: List["GastoRecorrente"] = Relationship(
        back_populates="organizacao"
    )
    # Configurações
    configuracoes: Dict = Field(
        default_factory=lambda: dict(
            {
                "converter_kg": False,
                "converter_kg_sempre": False,
                "usar_custo_med": False,
            }
        ),
        sa_column=Column(JSON),
    )

    class Config:
        arbitrary_types_allowed = True

    @property
    def plano_descricao(self):
        plano_data = getattr(PLANOS_DATA, self.plano.value)
        data_expiracao = self.plano_exiracao.strftime("%d/%m/%y")
        return f"{plano_data.app_descricao} (Expira em {data_expiracao})"

    @property
    def chave_pix_valida(self):
        try:
            pix_qr_code = PixQrCode(
                self.descricao, self.chave_pix, self.cidade, f"{10:.2f}"
            )
            return isinstance(pix_qr_code.export_base64(), str)
        except Exception as ex:
            return False


class RegistroOrganizacao(SQLModel, table=False):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    organizacao_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="organizacao.id"
    )
    data_criacao: datetime = Field(default=datetime.now(), nullable=False)

    def data_bs_payload(self):
        base_dict = self.model_dump()
        for key, value in base_dict.items():
            if isinstance(value, uuid.UUID):
                base_dict[key] = str(value)
        return base_dict

    def data_csv(self):
        base_dict = self.model_dump()

        safe_dict = {}

        for key in base_dict:
            if key in CSV_EXCLUDE_KEYS or key.endswith("_id"):
                continue
            safe_dict[key] = base_dict[key]

        for key, value in safe_dict.items():
            if isinstance(value, uuid.UUID):
                safe_dict[key] = str(value)
            elif isinstance(value, datetime):
                safe_dict[key] = value.strftime(STRFTIME_FORMAT)
        return safe_dict


class GastoRecorrente(RegistroOrganizacao, table=True):
    organizacao: "Organizacao" = Relationship(
        back_populates="gastos_recorrentes", sa_relationship_kwargs={"lazy": "selectin"}
    )
    descricao: str
    data_inicio: datetime = Field(default=datetime.now(), nullable=False)
    valor: float
    tipo: GastoTipo = Field(default=GastoTipo.FIXO, nullable=False)
    recorrencia: GastoRecorrencia = Field(
        default=GastoRecorrencia.MENSAL, nullable=False
    )

    def data_bs_payload(self):
        base_dict = self.model_dump()
        base_dict["data_inicio"] = self.data_inicio.strftime(STRFTIME_FORMAT)
        base_dict["data_criacao"] = self.data_criacao.strftime(STRFTIME_FORMAT)
        return base_dict


class Usuario(RegistroOrganizacao, table=True):
    organizacao: "Organizacao" = Relationship(
        back_populates="usuarios", sa_relationship_kwargs={"lazy": "selectin"}
    )
    nome: str
    email: str
    senha: Optional[str] = Field(default=None)
    dono: Optional[bool] = Field(default=False)
    administrador: Optional[bool] = Field(default=False)
    email_verificado: Optional[bool] = Field(default=False)

    def hash_senha(self) -> str:
        if not self.senha.startswith(
            "$2b$"
        ):  # Verifica se já está hasheada (evita rehash)
            self.senha = pwd_context.hash(self.senha)

    def verificar_senha(self, senha: str) -> bool:
        result = pwd_context.verify(senha, self.senha)
        return result

    def data_bs_payload(self):
        base_dict = self.model_dump()
        del base_dict["senha"]
        if self.administrador:  # pragma: nocover
            base_dict.update(organizacao_descricao="Administrador")
        base_dict.update(
            organizacao_descricao=(
                self.organizacao.descricao if self.organizacao else "-"
            )
        )
        base_dict["id"] = str(self.id)
        base_dict["organizacao_id"] = str(self.organizacao_id)
        base_dict["data_criacao"] = self.data_criacao.strftime(STRFTIME_FORMAT)
        return base_dict


class ReceitaGasto(RegistroOrganizacao, table=True):
    gasto_tipo: Optional[GastoTipo] = Field(None)
    gasto_valor: Optional[float] = Field(None)
    quantidade: Optional[float] = Field(default=None)
    receita_id: Optional[uuid.UUID] = Field(default=None, foreign_key="receita.id")
    insumo_id: Optional[uuid.UUID] = Field(default=None, foreign_key="insumo.id")
    receita: "Receita" = Relationship(
        back_populates="gastos", sa_relationship_kwargs={"lazy": "selectin"}
    )
    insumo: "Insumo" = Relationship(
        back_populates="receita_links", sa_relationship_kwargs={"lazy": "selectin"}
    )
    organizacao: "Organizacao" = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    descricao: Optional[str] = Field(default="Sem descrição")

    @validates("descricao")
    def convert_upper(self, key, value):
        if not value:
            if not self.insumo:
                return "Sem descrição"
            return self.insumo.nome
        return value

    @property
    def insumo_custo_p_grama(self):
        if self.organizacao.configuracoes["usar_custo_med"]:  # pragma: nocover
            return self.insumo.custo_p_grama_medio
        return self.insumo.custo_p_grama

    @property
    def custo(self):
        if not self.insumo:  # pragma: nocover
            return self.gasto_valor
        return round(self.quantidade * self.insumo_custo_p_grama, 2)

    @property
    def row(self):
        converter_kg = self.organizacao.configuracoes.get("converter_kg", False)
        converter_kg_sempre = self.organizacao.configuracoes.get(
            "converter_kg_sempre", False
        )

        col_descricao = self.descricao
        if self.insumo_id:
            col_descricao = self.insumo.nome

            if self.insumo:
                col_quantidade = filters.templates_filter_format_quantity(
                    self.quantidade,
                    converter_kg,
                    converter_kg_sempre,
                    unity=self.insumo.unidade,
                )
                col_custo_p_grama = filters.templates_filter_format_reais(
                    self.insumo_custo_p_grama
                )
                col_estoque_atual = filters.templates_filter_format_stock(
                    self.insumo.estoque_atual,
                    converter_kg,
                    converter_kg_sempre,
                    unity=self.insumo.unidade,
                )
                col_custo = filters.templates_filter_format_reais(self.custo)
                return [
                    col_descricao,
                    col_quantidade,
                    col_custo_p_grama,
                    col_custo,
                    col_estoque_atual,
                ]

        if self.gasto_tipo == GastoTipo.FIXO:
            col_custo = filters.templates_filter_format_reais(self.custo)
        elif self.gasto_tipo == GastoTipo.POR_UNIDADE:
            col_custo = filters.templates_filter_format_reais(self.custo) + "/un"
        else:
            col_custo = f"{self.custo}%"

        return [col_descricao, self.gasto_tipo.value.title(), col_custo]

    def data_csv(self):
        base_dict = super().data_csv()
        if self.insumo_id:
            base_dict["insumo"] = self.insumo.nome
        return base_dict

    def data_bs_payload(self):
        base_dict = self.model_dump()
        if self.gasto_tipo:
            base_dict["gasto_tipo"] = self.gasto_tipo.value
            base_dict["#input_gasto_valor_unidade"] = (
                "R$" if self.gasto_tipo == GastoTipo.FIXO else "%"
            )
        elif self.insumo:
            base_dict["insumo_id"] = str(self.insumo.id)
            base_dict["insumo_nome"] = self.insumo.nome
            base_dict["insumo_custo"] = self.insumo.custo
            base_dict["insumo_peso"] = self.insumo.peso
            base_dict["#input_quantidade_unidade"] = self.insumo.unidade
        base_dict["id"] = str(self.id)
        base_dict["organizacao_id"] = str(self.organizacao_id)
        base_dict["receita_id"] = str(self.receita_id)
        base_dict["data_criacao"] = self.data_criacao.strftime(STRFTIME_FORMAT)
        return base_dict


class Estoque(RegistroOrganizacao, table=True):
    descricao: Optional[str] = Field(default=None)
    insumo_id: Optional[uuid.UUID] = Field(default=None, foreign_key="insumo.id")
    insumo: "Insumo" = Relationship(
        back_populates="estoque_links", sa_relationship_kwargs={"lazy": "selectin"}
    )
    quantidade: Optional[float] = Field(default=0)
    valor_pago: Optional[float] = Field(default=0)
    organizacao: "Organizacao" = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    @classmethod
    def columns(self):
        return ["Data", "Descrição", "Valor Pago", "Insumo", "Quantidade"]

    @property
    def row(self):
        converter_kg = self.organizacao.configuracoes.get("converter_kg", False)
        converter_kg_sempre = self.organizacao.configuracoes.get(
            "converter_kg_sempre", False
        )

        col_valor_pago = filters.templates_filter_format_reais(self.valor_pago)
        if self.valor_pago:
            col_valor_pago = filters.status_html(
                "status-danger", col_valor_pago, "arrow_downward"
            )

        col_insumo = "-"
        if self.insumo_id:
            col_insumo = self.insumo.nome

        col_quantidade = filters.templates_filter_format_stock_movement(
            self.quantidade, converter_kg, converter_kg_sempre
        )
        col_data_criacao = filters.templates_filter_strftime(self.data_criacao)

        return [
            col_data_criacao,
            self.descricao,
            col_valor_pago,
            col_insumo,
            col_quantidade,
        ]

    def data_bs_payload(self):
        base_dict = self.model_dump()
        base_dict["data_criacao"] = self.data_criacao.strftime(STRFTIME_FORMAT)
        base_dict["id"] = str(self.id)
        base_dict["organizacao_id"] = str(self.organizacao_id)
        base_dict["insumo_id"] = str(self.insumo_id)
        return base_dict


class CaixaMovimentacao(RegistroOrganizacao, table=True):
    descricao: str
    valor: float
    tipo: CaixMovimentacaoTipo = Field(default=CaixMovimentacaoTipo.ENTRADA)
    recebido: bool = Field(default=False)
    organizacao: "Organizacao" = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    @classmethod
    def columns(self):
        return [
            "Data",
            "Descrição",
            "Tipo",
            "Valor",
            "Recebido",
        ]

    @property
    def row(self):
        try:
            col_data_criacao = filters.templates_filter_strftime(self.data_criacao)
            col_valor = filters.templates_filter_format_reais(self.valor)
            col_tipo = f"<code>{self.tipo.value}</code>"
            if self.tipo == CaixMovimentacaoTipo.ENTRADA:
                col_valor = filters.status_html(
                    "status-success", col_valor, "arrow_upward"
                )
            elif self.tipo == CaixMovimentacaoTipo.SAIDA:
                col_valor = filters.status_html(
                    "status-danger", col_valor, "arrow_downward"
                )
            else:
                col_valor = filters.status_html(
                    "status-secondary", col_valor, "more_horiz"
                )

            col_recebido = filters.templates_global_material_symbol(
                "more_horiz", "text-secondary"
            )
            if self.recebido:
                col_recebido = filters.templates_global_material_symbol(
                    "check", "text-success"
                )

            return [col_data_criacao, self.descricao, col_tipo, col_valor, col_recebido]
        except Exception as ex:
            logger.exception(ex)
            return []

    def data_bs_payload(self) -> dict:
        base_dict = self.model_dump()
        base_dict["data_criacao"] = self.data_criacao.strftime(STRFTIME_FORMAT)
        base_dict["#img_qr_code"] = self.gerar_qr_code()
        base_dict["tipo"] = self.tipo.value.title()
        base_dict["id"] = str(self.id)
        base_dict["organizacao_id"] = str(self.id)
        return base_dict

    def gerar_qr_code(self, pix_nome=None, pix_cidade=None, pix_chave=None) -> str:
        if not pix_nome:
            pix_nome = self.organizacao.descricao
        if not pix_cidade:
            pix_cidade = self.organizacao.cidade
        if not pix_chave:
            pix_chave = self.organizacao.chave_pix

        try:
            pix_qr_code = PixQrCode(
                pix_nome, pix_chave, pix_cidade, f"{self.valor:.2f}"
            )
            return pix_qr_code.export_base64()
        except Exception as ex:
            logger.error(ex)
            return None


class Insumo(RegistroOrganizacao, table=True):
    nome: str = Field(index=True)
    peso: float
    custo: float
    unidade: Optional[str] = "g"
    receita_links: List["ReceitaGasto"] = Relationship(
        back_populates="insumo", sa_relationship_kwargs={"lazy": "selectin"}
    )
    estoque_links: List["Estoque"] = Relationship(
        back_populates="insumo", sa_relationship_kwargs={"lazy": "selectin"}
    )
    organizacao: "Organizacao" = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    __table_args__ = (
        Index(
            "compound_insumo_nome_organizacao_id",
            "nome",
            "organizacao_id",
        ),
    )

    @classmethod
    def columns(self):
        return [
            "Id",
            "Nome",
            "Custo (R$)",
            "Un./Pct.",
            "Custo/un. (R$)",
            "Custo/un. méd. (R$)",
            "Estoque Atual",
            "Dt. Cadastro",
        ]

    @property
    def row(self):
        converter_kg = self.organizacao.configuracoes.get("converter_kg", False)
        converter_kg_sempre = self.organizacao.configuracoes.get(
            "converter_kg_sempre", False
        )

        col_custo = filters.templates_filter_format_reais(self.custo)
        col_peso = filters.templates_filter_format_quantity(
            self.peso, converter_kg, converter_kg_sempre, unity=self.unidade
        )

        col_custo_p_grama = filters.templates_filter_format_reais(self.custo_p_grama)
        col_custo_p_grama_medio = filters.templates_filter_format_reais(
            self.custo_p_grama_medio
        )

        col_estoque = filters.templates_filter_format_stock(
            self.estoque_atual, converter_kg, converter_kg_sempre, unity=self.unidade
        )

        col_data_criacao = filters.templates_filter_strftime(self.data_criacao)

        return [
            f"{str(self.id)[:10]}...",
            self.nome,
            col_custo,
            col_peso,
            col_custo_p_grama,
            col_custo_p_grama_medio,
            col_estoque,
            col_data_criacao,
        ]

    def data_bs_payload(self):
        base_dict = self.model_dump()
        receitas_associadas = []
        for r in self.receita_links:
            if not r.receita in receitas_associadas:
                receitas_associadas.append(r.receita)

        base_dict["#usado_em"] = [
            f"""
                <a href="/app/receitas/{r.id}">
                    <div class="card">
                        <div class="card-body">
                            {r.nome}<br>
                            <span class="text-muted">Clique para acessar</span>
                        </div>
                    </div>
                </a>
            """
            for r in receitas_associadas
            if r
        ]
        base_dict["estoque_atual"] = self.estoque_atual
        base_dict["id"] = str(self.id)
        base_dict["organizacao_id"] = str(self.organizacao_id)
        base_dict["data_criacao"] = self.data_criacao.strftime(STRFTIME_FORMAT)
        return base_dict

    @property
    def custo_p_grama_medio(self):
        if not self.estoque_links:
            return self.custo_p_grama
        estoques_com_preco = [
            (e.valor_pago / e.quantidade) for e in self.estoque_links if e.valor_pago
        ]
        return (
            sum(estoques_com_preco) / len(estoques_com_preco)
            if estoques_com_preco
            else self.custo_p_grama
        )

    @property
    def custo_p_grama(self):
        return self.custo / self.peso

    @property
    def estoque_atual(self):
        return sum([e.quantidade for e in self.estoque_links])


class Receita(RegistroOrganizacao, table=True):
    nome: str = Field(index=True)
    peso_unitario: float = 0
    peso_perda_por_processo: float = 0
    porcentagem_lucro: int = 33
    organizacao: "Organizacao" = Relationship()

    gastos: List["ReceitaGasto"] = Relationship(
        back_populates="receita", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def data_csv(self):
        base_data = super().data_csv()
        base_data["gastos"] = ",".join([str(g.data_csv()) for g in self.gastos])
        return base_data

    def data_bs_payload(self):
        base_dict = self.model_dump()
        base_dict["id"] = str(self.id)
        base_dict["organizacao_id"] = str(self.id)
        base_dict["data_criacao"] = self.data_criacao.strftime(STRFTIME_FORMAT)
        return base_dict

    __table_args__ = (
        Index(
            "compound_receita_nome_organizacao_id",
            "nome",
            "organizacao_id",
        ),
    )

    @classmethod
    def columns(self):
        return [
            "Nome",
            "Custo (R$)",
            "Rendimento (Un.)",
            "Preço Sug. (R$)",
            "Lucro Un.",
            "Reserva Un.",
        ]

    @property
    def row(self):
        try:
            col_rendimento = f"{self.rendimento_unidades} Un."
            col_custo_total = filters.templates_filter_format_reais(self.custo_total)
            col_preco_sug = filters.templates_filter_format_reais(self.preco_sugerido)

            lucro_un = (self.preco_sugerido - self.custo_unidade) / 2
            col_lucro_un = filters.status_html(
                "status-success", filters.templates_filter_format_reais(lucro_un)
            )
            col_reserva_un = filters.status_html(
                "status-success", filters.templates_filter_format_reais(lucro_un)
            )

            return [
                self.nome,
                col_custo_total,
                col_rendimento,
                col_preco_sug,
                col_lucro_un,
                col_reserva_un,
            ]
        except Exception as ex:
            logger.exception(ex)
            return [self.nome, "-", "-", "-", "-", "-"]

    @property
    def href(self):
        return f"/app/receitas/{self.id}"

    @validates("nome")
    def convert_upper(self, key, value):
        return value.upper()

    @property
    def faturamento(self):
        return self.preco_sugerido * self.rendimento_unidades

    @property
    def margem(self):
        return round(self.faturamento - self.custo_total, 2)

    @property
    def custo_base(self):
        return round(sum([g.custo for g in self.gastos if g.insumo]), 2)

    @property
    def custo_percentual(self):
        return round(
            sum([g.custo for g in self.gastos if g.gasto_tipo == GastoTipo.PERCENTUAL]),
            2,
        )

    @property
    def custo_fixo(self):
        return round(
            sum([g.custo for g in self.gastos if g.gasto_tipo == GastoTipo.FIXO]), 2
        )

    @property
    def custo_por_unidade(self):
        return round(
            sum(
                [g.custo for g in self.gastos if g.gasto_tipo == GastoTipo.POR_UNIDADE]
            ),
            2,
        )

    @property
    def custo_total(self):
        """Retorna a soma de custo dos insumos usados"""
        custo = self.custo_base + self.custo_fixo
        custo_percentual = (100 + self.custo_percentual) / 100
        return round(custo * custo_percentual, 2)

    @property
    def rendimento_bruto(self):
        """Retorna a soma da quantiadde dos insumos usados (em gramas)"""
        return max(
            1,
            round(
                sum(
                    [
                        i.quantidade
                        for i in self.gastos
                        if i.insumo and i.insumo.unidade == "g"
                    ]
                ),
                2,
            ),
        )

    @property
    def rendimento(self):
        """Retorna a soma da quantiadde dos insumos usados (em gramas)"""
        return self.rendimento_bruto - (
            self.peso_perda_por_processo if self.peso_perda_por_processo else 0
        )

    @property
    def rendimento_unidades(self):
        """Retorna a quantidade de unidades que a receita rende"""
        return (
            max(1, math.floor(self.rendimento / self.peso_unitario))
            if self.peso_unitario
            else 1
        )

    @property
    def custo_unidade(self):
        """Retorna o custo de cada unidade produzida"""
        return round(
            (self.custo_total / self.rendimento_unidades) + self.custo_por_unidade, 2
        )

    @property
    def preco_sugerido(self):
        """Retorna o preco a ser cobrado"""
        # custo_unidade  --  porcentagem_lucro
        # preco_final    --  100

        # 100 * self.custo_unidade = self.porcentagem_lucro * preco_final
        # preco_final = 100 * self.custo_unidade / self.porcentagem_lucro
        return math.ceil(100 * self.custo_unidade / self.porcentagem_lucro)
