from sqlalchemy import Column, Integer, String, DECIMAL, Enum, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base

class ContratoImposto(Base):
    """
    Configuração personalizada de alíquotas de impostos por contrato.
    Se não houver registro, usa-se o percentual padrão do contrato ou global.
    """
    __tablename__ = "contrato_impostos"
    __table_args__ = (
        PrimaryKeyConstraint("contrato_id", "tipo_imposto"),
    )

    contrato_id = Column(
        Integer,
        ForeignKey("contratos.id", ondelete="CASCADE"),
        nullable=False
    )
    tipo_imposto = Column(
        String(20),
        nullable=False,
        comment="ISS, INSS, IRRF, CSLL, PIS, COFINS"
    )
    aliquota = Column(DECIMAL(5, 2), nullable=False)
    base_calculo = Column(
        Enum("BRUTO", "LIQUIDO", name="base_calculo"),
        default="BRUTO",
        nullable=False
    )

    # Relacionamento
    contrato = relationship("Contrato", back_populates="impostos_config")