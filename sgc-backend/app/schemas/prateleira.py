from pydantic import BaseModel, field_validator
from typing import Optional, List
from decimal import Decimal
from datetime import date, datetime


# ─────────────────────────────────────────────────────────────
# PrateleiraExecucao Schemas
# ─────────────────────────────────────────────────────────────

class PrateleiraBase(BaseModel):
    descricao_servico: str
    data_execucao: date
    percentual_executado: Optional[Decimal] = None
    valor_estimado: Decimal
    observacoes: Optional[str] = None

    @field_validator("valor_estimado")
    @classmethod
    def valor_deve_ser_positivo(cls, v):
        if v <= 0:
            raise ValueError("Valor estimado deve ser maior que zero")
        return v

    @field_validator("percentual_executado")
    @classmethod
    def percentual_deve_ser_valido(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Percentual executado deve estar entre 0 e 100")
        return v


class PrateleiraCreate(PrateleiraBase):
    usuario_responsavel_id: Optional[int] = None


class PrateleiraUpdate(BaseModel):
    descricao_servico: Optional[str] = None
    data_execucao: Optional[date] = None
    percentual_executado: Optional[Decimal] = None
    valor_estimado: Optional[Decimal] = None
    observacoes: Optional[str] = None
    usuario_responsavel_id: Optional[int] = None

    @field_validator("valor_estimado")
    @classmethod
    def valor_deve_ser_positivo(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Valor estimado deve ser maior que zero")
        return v

    @field_validator("percentual_executado")
    @classmethod
    def percentual_deve_ser_valido(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Percentual executado deve estar entre 0 e 100")
        return v


class PrateleiraInDB(PrateleiraBase):
    id: int
    contrato_id: int
    valor_medido_acumulado: Decimal
    status: str
    cancelado_motivo: Optional[str] = None
    usuario_responsavel_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Campos calculados/extras (opcionais)
    contrato_numero: Optional[str] = None
    usuario_responsavel_nome: Optional[str] = None
    saldo_disponivel: Optional[Decimal] = None   # valor_estimado - valor_medido_acumulado

    class Config:
        from_attributes = True


class PrateleiraCancelar(BaseModel):
    motivo: str


# ─────────────────────────────────────────────────────────────
# BoletimPrateleiraExecucao Schemas (vínculo de medição)
# ─────────────────────────────────────────────────────────────

class VinculoPrateleiraCreate(BaseModel):
    prateleira_id: int
    valor_incluido: Decimal

    @field_validator("valor_incluido")
    @classmethod
    def valor_deve_ser_positivo(cls, v):
        if v <= 0:
            raise ValueError("Valor incluído deve ser maior que zero")
        return v


class VincularPrateleiraAoBoletimRequest(BaseModel):
    """Payload para vincular múltiplos itens da prateleira a um boletim."""
    vinculos: List[VinculoPrateleiraCreate]


class VinculoPrateleiraInDB(BaseModel):
    id: int
    boletim_id: int
    prateleira_id: int
    valor_incluido: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────
# Resumo da Prateleira (para dashboard e indicadores)
# ─────────────────────────────────────────────────────────────

class ResumoPrateleira(BaseModel):
    valor_total_em_prateleira: Decimal
    qtd_execucoes_pendentes: int
    qtd_execucoes_aguardando: int
    qtd_execucoes_antigas_30dias: int   # pendentes há mais de 30 dias
