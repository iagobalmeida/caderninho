from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel

from caderninho.src.domain.schemas import (
    CaixMovimentacaoTipo,
    GastoRecorrencia,
    GastoTipo,
    Planos,
)


class ReceitaAtualizar(BaseModel):
    id: UUID
    nome: str
    peso_unitario: float
    peso_perda_por_processo: float
    porcentagem_lucro: float


class ReceitaGastosAdicionar(BaseModel):
    receita_id: UUID
    insumo_id: Optional[UUID] = None
    descricao: Optional[str] = None
    quantidade: Optional[float] = None
    gasto_tipo: Optional[GastoTipo] = None  # TODO: Associar a ENUM
    gasto_valor: Optional[float] = None


class ReceitaGastosAtualizar(BaseModel):
    id: UUID
    receita_id: UUID
    insumo_id: UUID
    insumo_nome: Optional[str]
    insumo_custo: Optional[float]
    insumo_peso: Optional[float]
    quantidade: float


class ReceitaGastosRemover(BaseModel):
    receita_id: UUID
    selecionados_ids: str


class InsumoCriar(BaseModel):
    nome: str
    peso: float
    custo: float
    unidade: str


class InsumoAtualizar(InsumoCriar):
    id: UUID


class CaixaMovimentacaoCriar(BaseModel):
    descricao: str
    valor: float
    tipo: CaixMovimentacaoTipo


class CaixaMovimentacaoAtualizar(BaseModel):
    id: UUID
    descricao: str
    valor: float
    recebido: Optional[bool] = None


class EstoqueCriar(BaseModel):
    descricao: Optional[str] = None
    descricao_customizada: Optional[str] = None
    insumo_id: Optional[Union[str, UUID]] = None
    quantidade_insumo: Optional[Union[str, float]] = None
    receita_id: Optional[Union[UUID, str]] = None
    quantidade_receita: Optional[Union[str, float]] = None
    valor_pago: Optional[Union[str, float]] = None


class EstoqueAtualizar(BaseModel):
    id: UUID
    descricao: str
    valor_pago: float
    quantidade: float


class UsuarioAtualizar(BaseModel):
    id: UUID
    nome: str
    email: str
    senha: Optional[str] = None
    dono: bool


class UsuarioCriar(BaseModel):
    nome: str
    email: str
    senha: str
    plano: Optional[Planos] = None
    senha_confirmar: str
    organizacao_id: Optional[UUID] = None
    organizacao_descricao: Optional[str] = None
    dono: bool = False


class UsuarioEditar(BaseModel):
    id: UUID
    nome: str
    email: str
    nova_senha: str = None
    dono: bool = False


class AtualizarSenha(BaseModel):
    id: UUID
    senha_atual: str
    senha: str
    senha_confirmar: str


class GastoRecorrenteCriar(BaseModel):
    organizacao_id: str
    descricao: str
    data_inicio: datetime
    valor: float
    tipo: GastoTipo
    recorrencia: GastoRecorrencia
