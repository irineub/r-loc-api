from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models import TipoPessoa, TipoCobranca, StatusOrcamento, StatusLocacao

# Cliente Schemas
class ClienteBase(BaseModel):
    nome_razao_social: str = Field(..., min_length=1, max_length=200)
    endereco: Optional[str] = None
    telefone_comercial: Optional[str] = None
    telefone_ramal: Optional[str] = None
    telefone_celular: Optional[str] = None
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    rg: Optional[str] = None
    inscricao_municipal: Optional[str] = None
    inscricao_estadual: Optional[str] = None
    email: Optional[str] = None
    tipo_pessoa: TipoPessoa = TipoPessoa.FISICA
    observacoes: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(ClienteBase):
    nome_razao_social: Optional[str] = Field(None, min_length=1, max_length=200)

class Cliente(ClienteBase):
    id: int
    data_cadastro: datetime

    class Config:
        from_attributes = True

# Equipamento Schemas
class EquipamentoBase(BaseModel):
    descricao: str
    unidade: str
    preco_unitario: float
    estoque: int = 1
    estoque_alugado: int = 0

class EquipamentoCreate(EquipamentoBase):
    pass

class EquipamentoUpdate(BaseModel):
    descricao: Optional[str] = None
    unidade: Optional[str] = None
    preco_unitario: Optional[float] = None
    estoque: Optional[int] = None

class Equipamento(EquipamentoBase):
    id: int
    estoque_disponivel: int  # Calculado: estoque - estoque_alugado

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        # Calcular estoque_disponivel antes da serialização
        if hasattr(obj, 'estoque_disponivel'):
            obj.estoque_disponivel = obj.estoque - obj.estoque_alugado
        return super().from_orm(obj)

# ItemOrcamento Schemas
class ItemOrcamentoBase(BaseModel):
    equipamento_id: int
    quantidade: int = Field(..., gt=0)
    preco_unitario: float = Field(..., gt=0)
    dias: int = Field(..., gt=0)
    tipo_cobranca: str = Field(default='diaria')
    subtotal: float = Field(..., gt=0)

class ItemOrcamentoCreate(ItemOrcamentoBase):
    pass

class ItemOrcamento(ItemOrcamentoBase):
    id: int
    orcamento_id: int
    equipamento: Equipamento

    class Config:
        from_attributes = True

# Orcamento Schemas
class OrcamentoBase(BaseModel):
    cliente_id: int
    data_inicio: datetime
    data_fim: datetime
    desconto: float = Field(default=0.0, ge=0)
    frete: float = Field(default=0.0, ge=0)
    total_final: float = Field(..., gt=0)
    observacoes: Optional[str] = None

class OrcamentoCreate(OrcamentoBase):
    itens: List[ItemOrcamentoCreate]

class OrcamentoUpdate(BaseModel):
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    desconto: Optional[float] = Field(None, ge=0)
    frete: Optional[float] = Field(None, ge=0)
    total_final: Optional[float] = Field(None, gt=0)
    observacoes: Optional[str] = None

class Orcamento(OrcamentoBase):
    id: int
    status: StatusOrcamento
    data_criacao: datetime
    cliente: Cliente
    itens: List[ItemOrcamento]

    class Config:
        from_attributes = True

# ItemLocacao Schemas
class ItemLocacaoBase(BaseModel):
    equipamento_id: int
    quantidade: int = Field(..., gt=0)
    quantidade_devolvida: int | None = None
    preco_unitario: float = Field(..., gt=0)
    dias: int = Field(..., gt=0)
    subtotal: float = Field(..., gt=0)

class ItemLocacaoCreate(ItemLocacaoBase):
    pass

class ItemLocacao(ItemLocacaoBase):
    id: int
    locacao_id: int
    equipamento: Equipamento

    class Config:
        from_attributes = True

# Locacao Schemas
class LocacaoBase(BaseModel):
    orcamento_id: int
    cliente_id: int
    data_inicio: datetime
    data_fim: datetime
    total_final: float = Field(..., gt=0)
    observacoes: Optional[str] = None

class LocacaoCreate(LocacaoBase):
    itens: List[ItemLocacaoCreate]

class LocacaoUpdate(BaseModel):
    status: Optional[StatusLocacao] = None
    data_devolucao: Optional[datetime] = None
    observacoes: Optional[str] = None

class Locacao(LocacaoBase):
    id: int
    status: StatusLocacao
    data_devolucao: Optional[datetime] = None
    data_criacao: datetime
    orcamento: Orcamento
    cliente: Cliente
    itens: List[ItemLocacao]

    class Config:
        from_attributes = True

# Response Schemas
class OrcamentoResponse(BaseModel):
    orcamento: Orcamento
    message: str

class LocacaoResponse(BaseModel):
    locacao: Locacao
    message: str 