from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Enum,
    DECIMAL, Text, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class PrateleiraExecucao(Base):
    """
    Execuções realizadas em obra que ainda não foram incluídas em um Boletim de Medição.
    Representa o estágio intermediário: Contrato → Prateleira → Boletim de Medição.
    """
    __tablename__ = "prateleira_execucoes"
    __table_args__ = (
        Index("idx_prateleira_contrato_status", "contrato_id", "status"),
        Index("idx_prateleira_data_execucao", "data_execucao"),
    )

    id = Column(Integer, primary_key=True, index=True)

    contrato_id = Column(
        Integer,
        ForeignKey("contratos.id", ondelete="CASCADE"),
        nullable=False,
        comment="Contrato ao qual a execução pertence"
    )

    descricao_servico = Column(
        String(300),
        nullable=False,
        comment="Descrição do serviço executado"
    )

    data_execucao = Column(
        Date,
        nullable=False,
        comment="Data em que o serviço foi executado em campo"
    )

    percentual_executado = Column(
        DECIMAL(5, 2),
        nullable=True,
        comment="Percentual do serviço executado (0 a 100)"
    )

    valor_estimado = Column(
        DECIMAL(15, 2),
        nullable=False,
        comment="Valor estimado do serviço executado (R$)"
    )

    valor_medido_acumulado = Column(
        DECIMAL(15, 2),
        default=0,
        nullable=False,
        comment="Valor já incluído em Boletins de Medição (acumulado de medições parciais)"
    )

    status = Column(
        Enum(
            "PENDENTE",
            "AGUARDANDO_MEDICAO",
            "INCLUIDO_EM_MEDICAO",
            "CANCELADO",
            name="status_prateleira"
        ),
        default="PENDENTE",
        nullable=False,
        comment="PENDENTE=aguardando, AGUARDANDO_MEDICAO=pronto para medir, INCLUIDO_EM_MEDICAO=totalmente consumido, CANCELADO=cancelado"
    )

    observacoes = Column(Text, nullable=True)

    cancelado_motivo = Column(Text, nullable=True)

    usuario_responsavel_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=True,
        comment="Usuário responsável pelo registro da execução"
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    contrato = relationship("Contrato", back_populates="prateleiras")
    usuario_responsavel = relationship("Usuario", foreign_keys=[usuario_responsavel_id])
    vinculos_boletim = relationship(
        "BoletimPrateleiraExecucao",
        back_populates="prateleira",
        cascade="all, delete-orphan"
    )


class BoletimPrateleiraExecucao(Base):
    """
    Tabela de vínculo entre Boletins de Medição e itens da Prateleira.
    Permite medição parcial: um item pode ser vinculado a múltiplos boletins
    com valores diferentes, mantendo histórico completo.
    """
    __tablename__ = "boletim_prateleira_execucoes"
    __table_args__ = (
        UniqueConstraint("boletim_id", "prateleira_id", name="unique_boletim_prateleira"),
        Index("idx_bpe_prateleira_id", "prateleira_id"),
        Index("idx_bpe_boletim_id", "boletim_id"),
    )

    id = Column(Integer, primary_key=True, index=True)

    boletim_id = Column(
        Integer,
        ForeignKey("boletins_medicao.id", ondelete="CASCADE"),
        nullable=False,
        comment="Boletim de Medição que consumiu parte desta execução"
    )

    prateleira_id = Column(
        Integer,
        ForeignKey("prateleira_execucoes.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Item da prateleira vinculado ao boletim"
    )

    valor_incluido = Column(
        DECIMAL(15, 2),
        nullable=False,
        comment="Valor deste item que foi incluído neste boletim (pode ser parcial)"
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relacionamentos
    boletim = relationship("BoletimMedicao", back_populates="prateleira_vinculos")
    prateleira = relationship("PrateleiraExecucao", back_populates="vinculos_boletim")
