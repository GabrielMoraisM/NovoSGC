from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class ContratoArt(Base):
    __tablename__ = 'contrato_arts'

    id = Column(Integer, primary_key=True, index=True)
    contrato_id = Column(Integer, ForeignKey('contratos.id', ondelete='CASCADE'), nullable=False)
    nome_profissional = Column(String(100), nullable=False)
    numero_art = Column(String(30), nullable=False)
    finalizado = Column(Boolean, default=False)
    data_finalizacao = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relacionamento opcional (se você quiser acessar o contrato a partir da ART)
    contrato = relationship("Contrato", back_populates="arts")