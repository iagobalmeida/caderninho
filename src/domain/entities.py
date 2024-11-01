import math
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


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


class Ingrediente(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(index=True, unique=True)
    peso: float
    custo: float
    receita_links: List['ReceitaIngredienteLink'] = Relationship(back_populates='ingrediente')

    @property
    def custo_p_grama(self):
        return self.custo / self.peso


class Receita(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(index=True, unique=True)
    peso_unitario: float = 0
    porcentagem_lucro: int = 33

    ingrediente_links: List['ReceitaIngredienteLink'] = Relationship(back_populates='receita')

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

    def dict(self):
        custo_total = round(sum([i.custo for i in self.ingrediente_links]), 2)
        quantidade_total = max(1, round(sum([i.quantidade for i in self.ingrediente_links]), 2))
        custo_p_grama_total = round(custo_total/quantidade_total, 2)
        ingredientes = [
            *self.ingrediente_links,
            {
                'id': -1,
                'ingrediente': {
                    'nome': 'Total',
                    'custo_p_grama': custo_p_grama_total,
                },
                'quantidade': quantidade_total,
                'custo': custo_total
            }
        ]
        ret = {
            'id': self.id,
            'nome': self.nome,
            'custo_receita': self.custo,
            'rendimento_unidades': self.rendimento_unidades,
            'preco_sugerido': self.preco_sugerido,
            'faturamento': self.faturamento,
            'lucro': self.lucro,
            'rendimento': self.rendimento,
            'peso_unitario': self.peso_unitario,
            'custo_unidade': self.custo_unidade,
            'porcentagem_lucro': self.porcentagem_lucro,
            'ingredientes': ingredientes
        }
        return ret
