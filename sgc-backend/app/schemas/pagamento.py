from pydantic import BaseModel, validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

# ----------------------------------------------------------------------
# SCHEMA BASE
# ----------------------------------------------------------------------
class PagamentoBase(BaseModel):
    faturamento_id: int
    data_pagamento: date
    valor_pago: Decimal
    comprovante_url: Optional[str] = None
    observacao: Optional[str] = None

    @validator('valor_pago')
    def valida_valor(cls, v):
        if v <= 0:
            raise ValueError('Valor pago deve ser maior que zero')
        return v

# ----------------------------------------------------------------------
# SCHEMA PARA CRIAÇÃO (POST)
# ----------------------------------------------------------------------
class PagamentoCreate(PagamentoBase):
    pass

# ----------------------------------------------------------------------
# SCHEMA PARA ATUALIZAÇÃO (PUT/PATCH)
# ----------------------------------------------------------------------
class PagamentoUpdate(BaseModel):
    data_pagamento: Optional[date] = None
    valor_pago: Optional[Decimal] = None
    comprovante_url: Optional[str] = None
    observacao: Optional[str] = None

    @validator('valor_pago')
    def valida_valor(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Valor pago deve ser maior que zero')
        return v

# ----------------------------------------------------------------------
# SCHEMA PARA RESPOSTA (GET)
# ----------------------------------------------------------------------
class PagamentoInDB(PagamentoBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True