
import math
from datetime import datetime
from typing import Dict, List, Optional

from loguru import logger
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from pixqrcode import PixQrCode
from sqlalchemy.orm import validates
from sqlmodel import JSON, Column, Field, Relationship, SQLModel

from src.templates import filters

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

STRFTIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class Organizacao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    descricao: str
    cidade: Optional[str] = None
    chave_pix: Optional[str] = None
    usuarios: List['Usuario'] = Relationship(back_populates='organizacao')
    configuracoes: Dict = Field(default_factory=lambda: dict({
        'converter_kg': False,
        'converter_kg_sempre': False,
        'usar_custo_med': False
    }), sa_column=Column(JSON))

    class Config:
        arbitrary_types_allowed = True

    @property
    def chave_pix_valida(self):
        try:
            pix_qr_code = PixQrCode(self.descricao, self.chave_pix, self.cidade, f'{10:.2f}')
            return isinstance(pix_qr_code.export_base64(), str)
        except Exception as ex:
            return False


class RegistroOrganizacao(SQLModel, table=False):
    id: Optional[int] = Field(default=None, primary_key=True)
    organizacao_id: Optional[int] = Field(default=None, foreign_key="organizacao.id")


class Usuario(RegistroOrganizacao, table=True):
    organizacao: "Organizacao" = Relationship(back_populates="usuarios")
    nome: str
    email: str
    senha: Optional[str] = Field(default=None)
    dono: Optional[bool] = Field(default=False)
    administrador: Optional[bool] = Field(default=False)

    def hash_senha(self) -> str:
        if not self.senha.startswith("$2b$"):  # Verifica se já está hasheada (evita rehash)
            self.senha = pwd_context.hash(self.senha)

    def verificar_senha(self, senha: str) -> bool:
        result = pwd_context.verify(senha, self.senha)
        return result

    def dict(self):
        base_dict = self.model_dump()
        del base_dict['senha']
        if self.administrador:  # pragma: nocover
            base_dict.update(organizacao_descricao='Administrador')
        base_dict.update(
            organizacao_descricao=self.organizacao.descricao if self.organizacao else '-'
        )
        return base_dict


class ReceitaInsumoLink(RegistroOrganizacao, table=True):
    quantidade: float
    receita_id: Optional[int] = Field(default=None, foreign_key="receita.id")
    insumo_id: Optional[int] = Field(default=None, foreign_key="insumo.id")
    receita: "Receita" = Relationship(back_populates="insumo_links")
    insumo: "Insumo" = Relationship(back_populates="receita_links")
    organizacao: "Organizacao" = Relationship()

    @property
    def insumo_custo_p_grama(self):
        if self.organizacao.configuracoes['usar_custo_med']:  # pragma: nocover
            return self.insumo.custo_p_grama_medio
        return self.insumo.custo_p_grama

    @property
    def custo(self):
        if not self.insumo:  # pragma: nocover
            return 0
        return round(self.quantidade * self.insumo_custo_p_grama, 2)

    @property
    def row(self):
        converter_kg = self.organizacao.configuracoes.get('converter_kg', False)
        converter_kg_sempre = self.organizacao.configuracoes.get('converter_kg_sempre', False)

        col_quantidade = filters.templates_filter_format_quantity(self.quantidade, converter_kg, converter_kg_sempre, unity=self.insumo.unidade)
        col_custo_p_grama = filters.templates_filter_format_reais(self.insumo_custo_p_grama)
        col_custo = filters.templates_filter_format_reais(self.custo)
        col_estoque_atual = filters.templates_filter_format_stock(self.insumo.estoque_atual, converter_kg, converter_kg_sempre, unity=self.insumo.unidade)

        return [
            self.insumo.nome,
            col_quantidade,
            col_custo_p_grama,
            col_custo,
            col_estoque_atual
        ]

    def dict(self):
        base_dict = self.model_dump()
        base_dict['insumo_nome'] = self.insumo.nome
        base_dict['insumo_custo'] = self.insumo.custo
        base_dict['insumo_peso'] = self.insumo.peso
        base_dict['#input_quantidade_unidade'] = self.insumo.unidade
        return base_dict


class Estoque(RegistroOrganizacao, table=True):
    descricao: Optional[str] = Field(default=None)
    data_criacao: datetime = Field(default=datetime.now(), nullable=False)
    insumo_id: Optional[int] = Field(default=None, foreign_key="insumo.id")
    insumo: "Insumo" = Relationship(back_populates="estoque_links")
    quantidade: Optional[float] = Field(default=0)
    valor_pago: Optional[float] = Field(default=0)
    organizacao: "Organizacao" = Relationship()

    @classmethod
    def columns(self):
        return [
            'Data',
            'Descrição',
            'Valor Pago',
            'Insumo',
            'Quantidade'
        ]

    @property
    def row(self):
        converter_kg = self.organizacao.configuracoes.get('converter_kg', False)
        converter_kg_sempre = self.organizacao.configuracoes.get('converter_kg_sempre', False)

        col_valor_pago = filters.templates_filter_format_reais(self.valor_pago)

        col_insumo = '-'
        if self.insumo:
            col_insumo = self.insumo.nome

        col_quantidade = filters.templates_filter_format_quantity(self.quantidade, converter_kg, converter_kg_sempre)

        return [
            self.data_criacao.strftime(STRFTIME_FORMAT),
            self.descricao,
            col_valor_pago,
            col_insumo,
            col_quantidade
        ]

    def dict(self):
        base_dict = self.model_dump()
        base_dict['data_criacao'] = self.data_criacao.strftime(STRFTIME_FORMAT)
        return base_dict


class Venda(RegistroOrganizacao, table=True):
    data_criacao: datetime = Field(default=datetime.now(), nullable=False)
    descricao: str
    valor: float
    recebido: bool = Field(default=False)
    organizacao: "Organizacao" = Relationship()

    @classmethod
    def columns(self):
        return [
            'Data',
            'Descrição',
            'Valor',
            'Recebido',
        ]

    @property
    def row(self):
        col_data_criacao = self.data_criacao.strftime(STRFTIME_FORMAT)
        col_valor = filters.templates_filter_format_reais(self.valor)

        col_recebido = filters.templates_global_material_symbol('more_horiz', 'text-secondary')
        if self.recebido:
            col_recebido = filters.templates_global_material_symbol('check', 'text-success')

        return [
            col_data_criacao,
            self.descricao,
            col_valor,
            col_recebido
        ]

    def dict(self):
        base_dict = self.model_dump()
        base_dict['data_criacao'] = self.data_criacao.strftime(STRFTIME_FORMAT)
        base_dict['#img_qr_code'] = self.gerar_qr_code()
        return base_dict

    def gerar_qr_code(self, pix_nome=None, pix_cidade=None, pix_chave=None) -> str:
        if not pix_nome:
            pix_nome = self.organizacao.descricao
        if not pix_cidade:
            pix_cidade = self.organizacao.cidade
        if not pix_chave:
            pix_chave = self.organizacao.chave_pix

        try:
            pix_qr_code = PixQrCode(pix_nome, pix_chave, pix_cidade, f'{self.valor:.2f}')
            return pix_qr_code.export_base64()
        except Exception as ex:
            logger.exception(ex)
            return None


class Insumo(RegistroOrganizacao, table=True):
    nome: str = Field(index=True, unique=True)
    peso: float
    custo: float
    unidade: Optional[str] = 'g'
    receita_links: List['ReceitaInsumoLink'] = Relationship(back_populates='insumo')
    estoque_links: List['Estoque'] = Relationship(back_populates='insumo')
    organizacao: "Organizacao" = Relationship()

    @classmethod
    def columns(self):
        return [
            '#',
            'Nome',
            'Custo (R$)',
            'Un./Pct.',
            'Custo/un. (R$)',
            'Custo/un. méd. (R$)',
            'Estoque Atual',
        ]

    @property
    def row(self):
        converter_kg = self.organizacao.configuracoes.get('converter_kg', False)
        converter_kg_sempre = self.organizacao.configuracoes.get('converter_kg_sempre', False)

        col_custo = filters.templates_filter_format_reais(self.custo)
        col_peso = filters.templates_filter_format_quantity(self.peso, converter_kg, converter_kg_sempre, unity=self.unidade)

        col_custo_p_grama = filters.templates_filter_format_reais(self.custo_p_grama)
        col_custo_p_grama_medio = filters.templates_filter_format_reais(self.custo_p_grama_medio)

        col_estoque = filters.templates_filter_format_stock(self.estoque_atual, converter_kg, converter_kg_sempre, unity=self.unidade)

        return [
            self.id,
            self.nome,
            col_custo,
            col_peso,
            col_custo_p_grama,
            col_custo_p_grama_medio,
            col_estoque
        ]

    def dict(self):
        base_dict = self.model_dump()
        receitas_associadas = []
        for r in self.receita_links:
            if not r.receita in receitas_associadas:
                receitas_associadas.append(r.receita)

        base_dict['#usado_em'] = [
            f'''
                <a href="/app/receitas/{r.id}">
                    <div class="card">
                        <div class="card-body">
                            {r.nome}<br>
                            <span class="text-muted">Clique para acessar</span>
                        </div>
                    </div>
                </a>
            '''
            for r in receitas_associadas
        ]
        base_dict['estoque_atual'] = self.estoque_atual
        return base_dict

    @property
    def custo_p_grama_medio(self):
        if not self.estoque_links:
            return self.custo_p_grama
        estoques_com_preco = [(e.valor_pago/e.quantidade) for e in self.estoque_links if e.valor_pago]
        return sum(estoques_com_preco)/len(estoques_com_preco) if estoques_com_preco else self.custo_p_grama

    @property
    def custo_p_grama(self):
        return self.custo / self.peso

    @property
    def estoque_atual(self):
        return sum([e.quantidade for e in self.estoque_links])


class Receita(RegistroOrganizacao, table=True):
    nome: str = Field(index=True, unique=True)
    peso_unitario: float = 0
    porcentagem_lucro: int = 33
    organizacao: "Organizacao" = Relationship()

    insumo_links: List['ReceitaInsumoLink'] = Relationship(back_populates='receita')

    @classmethod
    def columns(self):
        return [
            'Nome',
            'Rendimento (Un.)',
            'Preço Sug. (R$)',
            'Custo (R$)',
            'Faturamento',
            'Lucro'
        ]

    @property
    def row(self):
        col_rendimento = f'{self.rendimento_unidades} Un.'
        col_preco_sug = filters.templates_filter_format_reais(self.preco_sugerido)
        col_custo = filters.templates_filter_format_reais(self.custo)
        col_faturamento = filters.templates_filter_format_reais(self.faturamento)
        col_lucro = filters.templates_filter_format_reais(self.lucro)

        return [
            self.nome,
            col_rendimento,
            col_preco_sug,
            col_custo,
            col_faturamento,
            col_lucro
        ]

    @property
    def href(self):
        return f'/app/receitas/{self.id}'

    @validates('nome')
    def convert_upper(self, key, value):
        return value.upper()

    @property
    def faturamento(self):
        return self.preco_sugerido*self.rendimento_unidades

    @property
    def lucro(self):
        return round(self.faturamento - self.custo, 2)

    @property
    def custo(self):
        '''Retorna a soma de custo dos insumos usados'''
        custo = sum([i.custo for i in self.insumo_links])
        return round(custo, 2)

    @property
    def rendimento(self):
        '''Retorna a soma da quantiadde dos insumos usados (em gramas)'''
        return max(1, round(sum([i.quantidade for i in self.insumo_links if i.insumo.unidade == 'g']), 2))

    @property
    def rendimento_unidades(self):
        '''Retorna a quantidade de unidades que a receita rende'''
        return max(1, math.ceil(self.rendimento/self.peso_unitario)) if self.peso_unitario else 1

    @property
    def custo_unidade(self):
        '''Retorna o custo de cada unidade produzida'''
        return round(self.custo/self.rendimento_unidades, 2)

    @property
    def preco_sugerido(self):
        '''Retorna o preco a ser cobrado'''
        porcentagem_custo = max(1, 100 - self.porcentagem_lucro)
        return math.ceil(self.custo_unidade*100/porcentagem_custo)
