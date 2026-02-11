from sqlalchemy import Column, Integer, Date, DateTime, DECIMAL, String, Text, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base

class Pagamento(Base):
    """
    Baixas financeiras (recebimentos) vinculadas a uma NF.
    """
    __tablename__ = "pagamentos"
    __table_args__ = (
        Index("idx_pagamento_faturamento_id", "faturamento_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    faturamento_id = Column(
        Integer,
        ForeignKey("faturamentos.id", ondelete="CASCADE"),
        nullable=False
    )
    data_pagamento = Column(Date, nullable=False)
    valor_pago = Column(DECIMAL(15, 2), nullable=False)
    comprovante_url = Column(String(255), nullable=True)
    observacao = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relacionamento
    faturamento = relationship("Faturamento", back_populates="pagamentos")