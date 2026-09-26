from pydantic import BaseModel, Field, BeforeValidator
from typing import Annotated, Optional, List, TypeVar, Generic
from datetime import datetime
from app.models import TipoPessoa, TipoCobranca, StatusOrcamento, StatusLocacao

# Colunas FLOAT com default 0.0 ainda podem ser NULL em registros antigos.
FloatZero = Annotated[float, BeforeValidator(lambda v: 0.0 if v is None else v)]

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
    preco_diaria: float = Field(..., ge=0)
    preco_semanal: float = Field(..., ge=0)
    preco_quinzenal: float = Field(..., ge=0)
    preco_mensal: float = Field(..., ge=0)
    estoque: int = 1
    estoque_alugado: int = 0

class EquipamentoCreate(EquipamentoBase):
    pass

class EquipamentoUpdate(BaseModel):
    descricao: Optional[str] = None
    unidade: Optional[str] = None
    preco_diaria: Optional[float] = Field(None, ge=0)
    preco_semanal: Optional[float] = Field(None, ge=0)
    preco_quinzenal: Optional[float] = Field(None, ge=0)
    preco_mensal: Optional[float] = Field(None, ge=0)
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
    quantidade: int = Field(..., ge=0)
    preco_unitario: float = Field(..., ge=0)
    dias: int = Field(..., ge=0)
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    tipo_cobranca: str = Field(default='diaria')
    subtotal: float = Field(..., ge=0)

class ItemOrcamentoCreate(ItemOrcamentoBase):
    pass

class ItemOrcamento(ItemOrcamentoBase):
    id: int
    orcamento_id: int
    # Pode ser None se houver FK órfã em bases antigas / dados migrados
    equipamento: Optional[Equipamento] = None

    class Config:
        from_attributes = True

# Orcamento Schemas
class OrcamentoBase(BaseModel):
    cliente_id: int
    data_inicio: datetime
    data_fim: datetime
    desconto: FloatZero = Field(default=0.0, ge=0)
    desconto_percentual: FloatZero = Field(default=0.0, ge=0, le=100)
    frete: FloatZero = Field(default=0.0, ge=0)
    total_final: float = Field(..., ge=0)
    observacoes: Optional[str] = None
    funcionario_id: Optional[int] = None

class OrcamentoCreate(OrcamentoBase):
    itens: List[ItemOrcamentoCreate]

class OrcamentoUpdate(BaseModel):
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    desconto: Optional[float] = Field(None, ge=0)
    desconto_percentual: Optional[float] = Field(None, ge=0, le=100)
    frete: Optional[float] = Field(None, ge=0)
    total_final: Optional[float] = Field(None, ge=0)
    observacoes: Optional[str] = None
    itens: Optional[List[ItemOrcamentoCreate]] = None
    status: Optional[StatusOrcamento] = None
    funcionario_id: Optional[int] = None

class Orcamento(OrcamentoBase):
    id: int
    status: StatusOrcamento
    data_criacao: datetime
    cliente: Optional[Cliente] = None
    funcionario: Optional['Funcionario'] = None
    itens: List[ItemOrcamento]

    class Config:
        from_attributes = True

# ItemLocacao Schemas
class ItemLocacaoBase(BaseModel):
    equipamento_id: int
    quantidade: int = Field(..., ge=0)
    quantidade_devolvida: int | None = None
    preco_unitario: float = Field(..., ge=0)
    dias: int = Field(..., ge=0)
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    subtotal: float = Field(..., ge=0)

class ItemLocacaoCreate(ItemLocacaoBase):
    pass

class ItemLocacao(ItemLocacaoBase):
    id: int
    locacao_id: int
    equipamento: Optional[Equipamento] = None

    class Config:
        from_attributes = True

# Locacao Schemas
class LocacaoBase(BaseModel):
    orcamento_id: int
    cliente_id: int
    data_inicio: datetime
    data_fim: datetime
    frete: Optional[float] = 0.0
    desconto: Optional[float] = 0.0
    desconto_percentual: Optional[float] = 0.0
    total_final: float = Field(..., ge=0)
    observacoes: Optional[str] = None
    endereco_entrega: Optional[str] = None
    funcionario_id: Optional[int] = None
    assinatura_realizada: bool = False
    assinatura_base64: Optional[str] = None
    locacao_original_id: Optional[int] = None

class LocacaoCreate(LocacaoBase):
    itens: List[ItemLocacaoCreate]

class LocacaoUpdate(BaseModel):
    status: Optional[StatusLocacao] = None
    data_devolucao: Optional[datetime] = None
    observacoes: Optional[str] = None
    endereco_entrega: Optional[str] = None
    funcionario_id: Optional[int] = None
    assinatura_realizada: Optional[bool] = None
    assinatura_base64: Optional[str] = None

class LocacaoUpdateAssinatura(BaseModel):
    assinatura_realizada: bool
    assinatura_base64: Optional[str] = None

class RenovarLocacaoItem(BaseModel):
    equipamento_id: int
    quantidade: int = Field(..., gt=0)
    data_fim: datetime
    tipo_cobranca: Optional[str] = None
    preco_unitario: Optional[float] = None
    subtotal: Optional[float] = None

class RenovarLocacaoRequest(BaseModel):
    data_inicio: datetime
    data_fim: datetime
    desconto: Optional[float] = 0.0
    desconto_percentual: Optional[float] = 0.0
    frete: Optional[float] = 0.0
    total_final: Optional[float] = 0.0
    itens: List[RenovarLocacaoItem]

class Locacao(LocacaoBase):
    id: int
    status: StatusLocacao
    data_devolucao: Optional[datetime] = None
    endereco_entrega: Optional[str] = None
    data_criacao: datetime
    orcamento: Optional[Orcamento] = None
    cliente: Optional[Cliente] = None
    funcionario: Optional['Funcionario'] = None
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

# Funcionario Schemas
class FuncionarioBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    nome: str = Field(..., min_length=1, max_length=200)
    ativo: bool = True

class FuncionarioCreate(FuncionarioBase):
    senha: str = Field(..., min_length=4)

class FuncionarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    senha: Optional[str] = Field(None, min_length=4)
    ativo: Optional[bool] = None

class FuncionarioLogin(BaseModel):
    username: str
    senha: str

class FuncionarioSenhaConsultaRequest(BaseModel):
    senha_autorizacao: str

class FuncionarioSenhaConsultaResponse(BaseModel):
    senha: Optional[str] = None
    message: Optional[str] = None

class Funcionario(FuncionarioBase):
    id: int
    data_cadastro: datetime

    class Config:
        from_attributes = True

# LogAuditoria Schemas
class LogAuditoriaBase(BaseModel):
    funcionario_username: Optional[str] = None
    acao: str
    entidade: str
    entidade_id: Optional[int] = None
    detalhes: Optional[str] = None

class LogAuditoriaCreate(LogAuditoriaBase):
    funcionario_id: Optional[int] = None

class LogAuditoria(LogAuditoriaBase):
    id: int
    funcionario_id: Optional[int] = None
    data_hora: datetime

    class Config:
        from_attributes = True

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int

class CorrigirEstoqueRequest(BaseModel):
    estoque: int = Field(..., ge=0)
    recalcular_alugado: bool = True
    estoque_alugado: Optional[int] = Field(None, ge=0)
    motivo: Optional[str] = None

class EquipamentoAlocacao(BaseModel):
    tipo: str  # locacao | orcamento
    id: int
    cliente_id: Optional[int] = None
    cliente_nome: Optional[str] = None
    quantidade: int
    quantidade_pendente: Optional[int] = None
    status: Optional[str] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None

class EquipamentoAlocacoesResponse(BaseModel):
    equipamento_id: int
    descricao: str
    estoque: int
    estoque_alugado: int
    estoque_disponivel: int
    alocacoes: List[EquipamentoAlocacao]

class DashboardCounts(BaseModel):
    clientes: int
    equipamentos: int
    orcamentos: int
    locacoes_ativas: int

class DashboardTopItem(BaseModel):
    nome: str
    totalLocacoes: int
    totalDias: Optional[int] = None
    totalValor: Optional[float] = None

class DashboardLocacaoResumo(BaseModel):
    id: int
    data_criacao: datetime
    status: StatusLocacao
    total_final: float
    cliente_id: int

class DashboardResumo(BaseModel):
    totais: DashboardCounts
    orcamentos_pendentes: List[Orcamento]
    locacoes_ativas: List[Locacao]
    top_equipamentos: List[DashboardTopItem]
    top_clientes: List[DashboardTopItem]
    locacoes_faturamento: List[DashboardLocacaoResumo]

# Resolve referências adiantadas (Funcionario) em todos os ambientes / versões do Pydantic
Orcamento.model_rebuild()
Locacao.model_rebuild()
OrcamentoResponse.model_rebuild()
LocacaoResponse.model_rebuild()
DashboardResumo.model_rebuild()