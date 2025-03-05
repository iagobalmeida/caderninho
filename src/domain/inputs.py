from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel

from src.domain.schemas import (CaixMovimentacaoTipo, GastoRecorrencia,
                                GastoTipo, Plano)


class ReceitaAtualizar(BaseModel):
    id: int
    nome: str
    peso_unitario: float
    porcentagem_lucro: float


class ReceitaGastosAdicionar(BaseModel):
    receita_id: int
    insumo_id: Optional[int] = None
    descricao: Optional[str] = None
    quantidade: Optional[float] = None
    gasto_tipo: Optional[GastoTipo] = None  # TODO: Associar a ENUM
    gasto_valor: Optional[float] = None


class ReceitaGastosAtualizar(BaseModel):
    id: int
    receita_id: int
    insumo_id: int
    insumo_nome: Optional[str]
    insumo_custo: Optional[float]
    insumo_peso: Optional[float]
    quantidade: float


class ReceitaGastosRemover(BaseModel):
    receita_id: int
    selecionados_ids: str


class InsumoCriar(BaseModel):
    nome: str
    peso: float
    custo: float
    unidade: str


class InsumoAtualizar(InsumoCriar):
    id: int


class CaixaMovimentacaoCriar(BaseModel):
    descricao: str
    valor: float
    tipo: CaixMovimentacaoTipo


class CaixaMovimentacaoAtualizar(BaseModel):
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
    plano: Optional[Plano] = None
    senha_confirmar: str
    organizacao_id:  Optional[int] = False
    organizacao_descricao: Optional[str] = None
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


class GastoRecorrenteCriar(BaseModel):
    organizacao_id: int
    descricao: str
    data_inicio: datetime
    valor: float
    tipo: GastoTipo
    recorrencia: GastoRecorrencia
