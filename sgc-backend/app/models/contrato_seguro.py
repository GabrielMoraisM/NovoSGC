from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, DECIMAL, ForeignKey, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class ContratoSeguro(Base):
    __tablename__ = 'contrato_seguros'

    id = Column(Integer, primary_key=True, index=True)
    contrato_id = Column(Integer, ForeignKey('contratos.id', ondelete='CASCADE'), nullable=False)
    seguradora_id = Column(Integer, ForeignKey('empresas.id', ondelete='RESTRICT'), nullable=False)
    tipo = Column(
        Enum('LICITACAO', 'CONTRATO', 'RESPONSABILIDADE_CIVIL', 'RISCO_PROFISSIONAL', 'RISCO_ENGENHARIA', 'GARANTIA_CONTRATUAL_RETOMADA', name='tipo_seguro'),
        nullable=False
    )
    numero_apolice = Column(String(50), nullable=True)
    data_vencimento = Column(Date, nullable=False)
    valor = Column(DECIMAL(15,2), nullable=True)
    cliente_id = Column(Integer, ForeignKey('empresas.id', ondelete='RESTRICT'), nullable=False)
    tomador_id = Column(Integer, ForeignKey('empresas.id', ondelete='RESTRICT'), nullable=False)
    objeto_segurado = Column(Text, nullable=True)
    possui_clausula_retomada = Column(Boolean, default=False)
    observacoes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # relacionamentos (opcionais)
    contrato = relationship('Contrato', back_populates='seguros')
    seguradora = relationship('Empresa', foreign_keys=[seguradora_id])
    cliente = relationship('Empresa', foreign_keys=[cliente_id])
    tomador = relationship('Empresa', foreign_keys=[tomador_id])