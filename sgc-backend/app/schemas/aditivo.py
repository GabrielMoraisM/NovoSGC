from pydantic import BaseModel, validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

# ----------------------------------------------------------------------
# SCHEMA BASE
# ----------------------------------------------------------------------
class AditivoBase(BaseModel):
    tipo: str  # 'PRAZO', 'VALOR', 'AMBOS', 'PARALISACAO'
    numero_emenda: Optional[str] = None
    data_aprovacao: Optional[date] = None
    dias_acrescimo: int = 0
    valor_acrescimo: Decimal = 0
    justificativa: Optional[str] = None

    @validator('tipo')
    def valida_tipo(cls, v):
        allowed = ('PRAZO', 'VALOR', 'AMBOS', 'PARALISACAO')
        if v not in allowed:
            raise ValueError(f'Tipo deve ser um de {allowed}')
        return v

    @validator('dias_acrescimo')
    def valida_dias(cls, v, values):
        if 'tipo' in values and values['tipo'] in ('PRAZO', 'AMBOS', 'PARALISACAO'):
            # pode ser negativo (redução de prazo)
            pass
        return v

    @validator('valor_acrescimo')
    def valida_valor(cls, v, values):
        if 'tipo' in values and values['tipo'] in ('VALOR', 'AMBOS'):
            # pode ser negativo (redução de valor)
            pass
        return v

# ----------------------------------------------------------------------
# SCHEMA PARA CRIAÇÃO (POST)
# ----------------------------------------------------------------------
class AditivoCreate(AditivoBase):
    contrato_id: int

# ----------------------------------------------------------------------
# SCHEMA PARA ATUALIZAÇÃO (PUT/PATCH)
# ----------------------------------------------------------------------
class AditivoUpdate(BaseModel):
    tipo: Optional[str] = None
    numero_emenda: Optional[str] = None
    data_aprovacao: Optional[date] = None
    dias_acrescimo: Optional[int] = None
    valor_acrescimo: Optional[Decimal] = None
    justificativa: Optional[str] = None

    @validator('tipo')
    def valida_tipo(cls, v):
        if v is None:
            return v
        allowed = ('PRAZO', 'VALOR', 'AMBOS', 'PARALISACAO')
        if v not in allowed:
            raise ValueError(f'Tipo deve ser um de {allowed}')
        return v

# ----------------------------------------------------------------------
# SCHEMA PARA RESPOSTA (GET)
# ----------------------------------------------------------------------
class AditivoInDB(AditivoBase):
    id: int
    contrato_id: int
    created_at: datetime

    class Config:
        from_attributes = True