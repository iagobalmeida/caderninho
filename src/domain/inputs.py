from typing import Optional, Union

from pydantic import BaseModel


class ReceitaAtualizar(BaseModel):
    id: int
    nome: str
    peso_unitario: float
    porcentagem_lucro: float


class ReceitaIngredienteAdicionar(BaseModel):
    id: int
    ingrediente_id: int
    quantidade: float


class ReceitaIngredienteAtualizar(BaseModel):
    id: int
    ingrediente_id: int
    quantidade: float


class ReceitaIngredienteRemover(BaseModel):
    id: int
    ingrediente_id: int


class IngredienteCriar(BaseModel):
    nome: str
    peso: float
    custo: float


class IngredienteAtualizar(IngredienteCriar):
    id: int


class VendaCriar(BaseModel):
    descricao: str
    valor: float


class VendaAtualizar(VendaCriar):
    id: int


class EstoqueCriar(BaseModel):
    descricao: Optional[str] = None
    ingrediente_id: Optional[int] = None
    quantidade: Optional[Union[str, float]] = None
    valor_pago: Optional[float] = None


class EstoqueAtualizar(BaseModel):
    id: int
