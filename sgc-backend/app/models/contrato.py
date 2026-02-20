from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, DECIMAL, ForeignKey, Index, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base

class Contrato(Base):
    """
    Representa um contrato de obra, consórcio ou SCP.
    É a entidade central do sistema.
    """
    __tablename__ = "contratos"

    # ------------------------------------------------------------
    # Chave primária
    # ------------------------------------------------------------
    id = Column(Integer, primary_key=True, index=True)

    # ------------------------------------------------------------
    # Dados gerais do contrato
    # ------------------------------------------------------------
    numero_contrato = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Número único do contrato (ex: 128/2024)"
    )

    tipo_obra = Column(
        Enum("HECA_100", "CONSORCIO", "SCP", name="tipo_obra"),
        nullable=False,
        comment="HECA_100 = obra própria, CONSORCIO = consórcio, SCP = Sociedade em Conta de Participação"
    )

    valor_original = Column(
        DECIMAL(15, 2),
        nullable=False,
        comment="Valor inicial do contrato (R$)"
    )

    prazo_original_dias = Column(
        Integer,
        nullable=False,
        comment="Prazo em dias corridos (sem considerar aditivos)"
    )

    data_inicio = Column(
        Date,
        nullable=False,
        comment="Data de início da obra (marco zero para cálculos)"
    )

    data_fim_prevista = Column(
        Date,
        nullable=True,
        comment="Data prevista de término (calculada: data_inicio + prazo_original + soma dos aditivos de prazo)"
    )
    
    valor_total = Column(DECIMAL(15,2), nullable=True)   # valor original + soma dos aditivos
 # valor original + aditivos


    # ------------------------------------------------------------
    # Status e configurações
    # ------------------------------------------------------------
    status = Column(
        Enum("ATIVO", "PARALISADO", "ENCERRADO", name="status_contrato"),
        default="ATIVO",
        nullable=False,
        comment="Situação atual do contrato"
    )

    iss_percentual_padrao = Column(
        DECIMAL(5, 2),
        nullable=True,
        comment="Alíquota padrão de ISS para este contrato (pode ser sobrescrita em contrato_impostos)"
    )

    # ------------------------------------------------------------
    # Chave estrangeira: cliente (tabela empresas)
    # ------------------------------------------------------------
    cliente_id = Column(
        Integer,
        ForeignKey("empresas.id", ondelete="RESTRICT"),
        nullable=False,
        comment="ID do cliente (tomador do serviço) – deve ser uma empresa com tipo = 'CLIENTE'"
    )
    
    numero_os = Column(String(50), nullable=True)
    data_os = Column(Date, nullable=True)
    descricao_os = Column(Text, nullable=True)

    gestor = Column(String(100), nullable=True)
    
    # ------------------------------------------------------------
    # Auditoria
    # ------------------------------------------------------------
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # ------------------------------------------------------------
    # Relacionamentos (serão populados quando criarmos os outros modelos)
    # ------------------------------------------------------------
    cliente = relationship("Empresa", foreign_keys=[cliente_id])

    # Um contrato pode ter vários aditivos
    aditivos = relationship("Aditivo", back_populates="contrato", cascade="all, delete-orphan")

    # Participantes do consórcio/SCP
    participantes = relationship("ContratoParticipante", back_populates="contrato", cascade="all, delete-orphan")

    # ARTs (responsáveis técnicos)
    arts = relationship("ContratoArt", back_populates="contrato", cascade="all, delete-orphan")

    # Seguros / garantias
    seguros = relationship("ContratoSeguro", back_populates="contrato", cascade="all, delete-orphan")

    # Boletins de Medição
    boletins = relationship("BoletimMedicao", back_populates="contrato", cascade="all, delete-orphan")

    # Configurações personalizadas de impostos
    impostos_config = relationship("ContratoImposto", back_populates="contrato", cascade="all, delete-orphan")

    # Usuários com permissão de acesso (RLS)
    usuarios = relationship("UsuarioContrato", back_populates="contrato", cascade="all, delete-orphan")

    # ------------------------------------------------------------
    # Índices adicionais (além do PK e do unique)
    # ------------------------------------------------------------
    __table_args__ = (
        Index("idx_contratos_status", "status"),
        Index("idx_contratos_cliente_id", "cliente_id"),
    )