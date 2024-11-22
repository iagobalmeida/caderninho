from typing import List, Optional, Union

from pydantic import BaseModel


class ReceitaAtualizar(BaseModel):
    id: int
    nome: str
    peso_unitario: float
    porcentagem_lucro: float


class ReceitaIngredienteAdicionar(BaseModel):
    receita_id: int
    ingrediente_id: int
    quantidade: float


class ReceitaIngredienteAtualizar(BaseModel):
    id: int
    receita_id: int
    ingrediente_id: int
    ingrediente_nome: Optional[str]
    ingrediente_custo: Optional[float]
    ingrediente_peso: Optional[float]
    quantidade: float


class ReceitaIngredienteRemover(BaseModel):
    receita_id: int
    selecionados_ids: str


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
    descricao_customizada: Optional[str] = None
    ingrediente_id: Optional[int] = None
    quantidade_ingrediente: Optional[Union[str, float]] = None
    receita_id: Optional[int] = None
    quantidade_receita: Optional[Union[str, float]] = None
    valor_pago: Optional[Union[str, float]] = None


class EstoqueAtualizar(BaseModel):
    id: int
    descricao: str
    valor_pago: float
    quantidade: float


class UsuarioAtualizar(BaseModel):
    id: int
    nome: str
    email: str


class UsuarioCriar(BaseModel):
    nome: str
    email: str
    senha: str
    senha_confirmar: str
    organizacao_id:  Optional[int] = False
    organizacao_descricao: Optional[str] = False
    dono: bool = False


class UsuarioEditar(BaseModel):
    id: int
    nome: str
    email: str
    nova_senha: str = None
    dono: bool = False


class AlterarSenha(BaseModel):
    id: int
    senha_atual: str
    senha: str
    senha_confirmar: str
