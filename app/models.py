from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum
import hashlib

class TipoPessoa(str, enum.Enum):
    FISICA = "fisica"
    JURIDICA = "juridica"

class TipoCobranca(str, enum.Enum):
    DIARIA = "diaria"
    SEMANAL = "semanal"
    QUINZENAL = "quinzenal"
    MENSAL = "mensal"

class StatusOrcamento(str, enum.Enum):
    PENDENTE = "pendente"
    APROVADO = "aprovado"
    REJEITADO = "rejeitado"

class StatusLocacao(str, enum.Enum):
    ATIVA = "ativa"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"
    ATRASADA = "atrasada"

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome_razao_social = Column(String(200), nullable=False)
    endereco = Column(Text)
    telefone_comercial = Column(String(20))
    telefone_ramal = Column(String(10))
    telefone_celular = Column(String(20))
    cpf = Column(String(14))
    cnpj = Column(String(18))
    rg = Column(String(20))
    inscricao_municipal = Column(String(20))
    inscricao_estadual = Column(String(20))
    email = Column(String(100))
    tipo_pessoa = Column(Enum(TipoPessoa), default=TipoPessoa.FISICA)
    data_cadastro = Column(DateTime(timezone=True), server_default=func.now())
    observacoes = Column(Text)

    # Relationships
    orcamentos = relationship("Orcamento", back_populates="cliente")
    locacoes = relationship("Locacao", back_populates="cliente")

class Equipamento(Base):
    __tablename__ = "equipamentos"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, nullable=False)
    unidade = Column(String, nullable=False)
    preco_diaria = Column(Float, nullable=False)
    preco_semanal = Column(Float, nullable=False)
    preco_quinzenal = Column(Float, nullable=False)
    preco_mensal = Column(Float, nullable=False)
    estoque = Column(Integer, default=1, nullable=False)  # Quantidade disponível em estoque
    estoque_alugado = Column(Integer, default=0, nullable=False)  # Quantidade atualmente alugada

    # Relationships
    itens_orcamento = relationship("ItemOrcamento", back_populates="equipamento")

    @property
    def estoque_disponivel(self):
        return self.estoque - self.estoque_alugado

class Orcamento(Base):
    __tablename__ = "orcamentos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=False)
    desconto = Column(Float, default=0.0)
    frete = Column(Float, default=0.0)
    total_final = Column(Float, nullable=False)
    status = Column(Enum(StatusOrcamento), default=StatusOrcamento.PENDENTE)
    observacoes = Column(Text)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    cliente = relationship("Cliente", back_populates="orcamentos")
    itens = relationship("ItemOrcamento", back_populates="orcamento")
    locacao = relationship("Locacao", back_populates="orcamento", uselist=False)

class ItemOrcamento(Base):
    __tablename__ = "itens_orcamento"

    id = Column(Integer, primary_key=True, index=True)
    orcamento_id = Column(Integer, ForeignKey("orcamentos.id"), nullable=False)
    equipamento_id = Column(Integer, ForeignKey("equipamentos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Float, nullable=False)
    dias = Column(Integer, nullable=False)
    tipo_cobranca = Column(Enum('diaria', 'semanal', 'quinzenal', 'mensal', name='tipo_cobranca_item'), nullable=False, default='diaria')
    subtotal = Column(Float, nullable=False)

    # Relationships
    orcamento = relationship("Orcamento", back_populates="itens")
    equipamento = relationship("Equipamento", back_populates="itens_orcamento")

class Locacao(Base):
    __tablename__ = "locacoes"

    id = Column(Integer, primary_key=True, index=True)
    orcamento_id = Column(Integer, ForeignKey("orcamentos.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=False)
    status = Column(Enum(StatusLocacao), default=StatusLocacao.ATIVA)
    total_final = Column(Float, nullable=False)
    observacoes = Column(Text)
    data_devolucao = Column(DateTime)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    orcamento = relationship("Orcamento", back_populates="locacao")
    cliente = relationship("Cliente", back_populates="locacoes")
    itens = relationship("ItemLocacao", back_populates="locacao")

class ItemLocacao(Base):
    __tablename__ = "itens_locacao"

    id = Column(Integer, primary_key=True, index=True)
    locacao_id = Column(Integer, ForeignKey("locacoes.id"), nullable=False)
    equipamento_id = Column(Integer, ForeignKey("equipamentos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    quantidade_devolvida = Column(Integer, nullable=False, default=0)
    preco_unitario = Column(Float, nullable=False)
    dias = Column(Integer, nullable=False)
    subtotal = Column(Float, nullable=False)

    # Relationships
    locacao = relationship("Locacao", back_populates="itens")
    equipamento = relationship("Equipamento")

class Funcionario(Base):
    __tablename__ = "funcionarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    nome = Column(String(200), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    data_cadastro = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    logs = relationship("LogAuditoria", back_populates="funcionario")

    def verificar_senha(self, senha: str) -> bool:
        """Verifica se a senha fornecida corresponde ao hash armazenado"""
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        return senha_hash == self.senha_hash

    @staticmethod
    def hash_senha(senha: str) -> str:
        """Gera o hash da senha"""
        return hashlib.sha256(senha.encode()).hexdigest()

class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"

    id = Column(Integer, primary_key=True, index=True)
    funcionario_id = Column(Integer, ForeignKey("funcionarios.id"), nullable=True)
    funcionario_username = Column(String(50), nullable=True)  # Para manter histórico mesmo se funcionário for deletado
    acao = Column(String(100), nullable=False)  # Ex: "criar_orcamento", "atualizar_cliente", etc
    entidade = Column(String(50), nullable=False)  # Ex: "orcamento", "cliente", "equipamento", etc
    entidade_id = Column(Integer, nullable=True)  # ID da entidade afetada
    detalhes = Column(Text)  # Detalhes adicionais da ação
    data_hora = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    funcionario = relationship("Funcionario", back_populates="logs") 