from typing import List, Optional, Union

from pydantic import BaseModel


class ReceitaAtualizar(BaseModel):
    id: int
    nome: str
    peso_unitario: float
    porcentagem_lucro: float


class ReceitaInsumoAdicionar(BaseModel):
    receita_id: int
    insumo_id: int
    quantidade: float


class ReceitaInsumoAtualizar(BaseModel):
    id: int
    receita_id: int
    insumo_id: int
    insumo_nome: Optional[str]
    insumo_custo: Optional[float]
    insumo_peso: Optional[float]
    quantidade: float


class ReceitaInsumoRemover(BaseModel):
    receita_id: int
    selecionados_ids: str


class InsumoCriar(BaseModel):
    nome: str
    peso: float
    custo: float
    unidade: str


class InsumoAtualizar(InsumoCriar):
    id: int


class VendaCriar(BaseModel):
    descricao: str
    valor: float


class VendaAtualizar(VendaCriar):
    id: int
    descricao: str
    valor: float
    recebido: Optional[bool] = None


class EstoqueCriar(BaseModel):
    descricao: Optional[str] = None
    descricao_customizada: Optional[str] = None
    insumo_id: Optional[int] = None
    quantidade_insumo: Optional[Union[str, float]] = None
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
    senha: Optional[str] = None
    dono: bool


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


class AtualizarSenha(BaseModel):
    id: int
    senha_atual: str
    senha: str
    senha_confirmar: str
