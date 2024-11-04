import math
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import validates
from sqlmodel import Field, Relationship, SQLModel, text


class ReceitaIngredienteLink(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
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


class Estoque(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    data_criacao: datetime = Field(sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")})
    ingrediente_id: Optional[int] = Field(default=None, foreign_key="ingrediente.id")
    ingrediente: "Ingrediente" = Relationship(back_populates="estoque_links")
    quantidade: float
    valor_pago: Optional[float] = Field(default=0)


class Venda(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    data_criacao: datetime = Field(sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")})
    descricao: str
    valor: float


class Ingrediente(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
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


class Receita(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
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
