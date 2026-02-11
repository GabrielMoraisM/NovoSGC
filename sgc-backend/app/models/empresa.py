from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship  # <-- ESTA LINHA ESTAVA FALTANDO

from app.db.base import Base

class Empresa(Base):
    """
    Cadastro de todas as pessoas jurídicas envolvidas no sistema:
    - Heca (matriz/filiais)
    - Parceiros de consórcio / SCP
    - Clientes
    - Seguradoras
    """
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True)
    razao_social = Column(String(200), nullable=False)
    cnpj = Column(String(18), unique=True, nullable=False)
    tipo = Column(
        Enum("MATRIZ", "FILIAL", "PARCEIRO_CONSORCIO", "SCP", "CLIENTE", name="tipo_empresa"),
        nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
        # Contratos onde a empresa é cliente
    contratos_como_cliente = relationship("Contrato", foreign_keys="Contrato.cliente_id", back_populates="cliente")
    
    # Participações em consórcios/SCP
    participacoes = relationship("ContratoParticipante", back_populates="empresa", cascade="all, delete-orphan")
    
    # Contratos onde a empresa é seguradora
    seguradoras = relationship("ContratoSeguro", foreign_keys="ContratoSeguro.seguradora_id", back_populates="seguradora")
    
    # NFs emitidas (empresa emissora)
    notas_emitidas = relationship("Faturamento", foreign_keys="Faturamento.empresa_emissora_id", back_populates="empresa_emissora")
    
    # NFs como tomador (cliente)
    notas_recebidas = relationship("Faturamento", foreign_keys="Faturamento.cliente_id", back_populates="cliente")

    # Futuros relacionamentos:
    # contratos_como_cliente = relationship("Contrato", foreign_keys="Contrato.cliente_id", back_populates="cliente")
    # participacoes = relationship("ContratoParticipante", back_populates="empresa")
    # seguradoras = relationship("ContratoSeguro", foreign_keys="ContratoSeguro.seguradora_id", back_populates="seguradora")