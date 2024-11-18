import math
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import validates
from sqlmodel import Field, Relationship, SQLModel


class Organizacao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    descricao: str
    usuarios: List['Usuario'] = Relationship(back_populates='organizacao')


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


class ReceitaIngredienteLink(RegistroOrganizacao, table=True):
    quantidade: float
    receita_id: Optional[int] = Field(default=None, foreign_key="receita.id")
    ingrediente_id: Optional[int] = Field(default=None, foreign_key="ingrediente.id")
    receita: "Receita" = Relationship(back_populates="ingrediente_links")
    ingrediente: "Ingrediente" = Relationship(back_populates="receita_links")

    @property
    def custo(self):
        if not self.ingrediente:
            return 0
        return round(self.quantidade * self.ingrediente.custo_p_grama, 2)

    def dict(self):
        base_dict = self.model_dump()
        base_dict['ingrediente_nome'] = self.ingrediente.nome
        base_dict['ingrediente_custo'] = self.ingrediente.custo
        base_dict['ingrediente_peso'] = self.ingrediente.peso
        return base_dict


class Estoque(RegistroOrganizacao, table=True):
    descricao: Optional[str] = Field(default=None)
    data_criacao: datetime = Field(default=datetime.now(), nullable=False)
    ingrediente_id: Optional[int] = Field(default=None, foreign_key="ingrediente.id")
    ingrediente: "Ingrediente" = Relationship(back_populates="estoque_links")
    quantidade: Optional[float] = Field(default=0)
    valor_pago: Optional[float] = Field(default=0)


class Venda(RegistroOrganizacao, table=True):
    data_criacao: datetime = Field(default=datetime.now(), nullable=False)
    descricao: str
    valor: float


class Ingrediente(RegistroOrganizacao, table=True):
    nome: str = Field(index=True, unique=True)
    peso: float
    custo: float
    receita_links: List['ReceitaIngredienteLink'] = Relationship(back_populates='ingrediente')
    estoque_links: List['Estoque'] = Relationship(back_populates='ingrediente')

    @property
    def custo_p_grama_medio(self):
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

    ingrediente_links: List['ReceitaIngredienteLink'] = Relationship(back_populates='receita')

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
        '''Retorna a soma de custo dos ingredientes usados'''
        custo = sum([i.custo for i in self.ingrediente_links])
        return round(custo, 2)

    @property
    def rendimento(self):
        '''Retorna a soma da quantiadde dos ingredientes usados (em gramas)'''
        return max(1, round(sum([i.quantidade for i in self.ingrediente_links]), 2))

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
