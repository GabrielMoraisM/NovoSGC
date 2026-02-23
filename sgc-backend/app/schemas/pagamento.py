from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

class PagamentoBase(BaseModel):
    faturamento_id: int
    data_pagamento: date
    valor_pago: Decimal
    comprovante_url: Optional[str] = None
    observacao: Optional[str] = None

class PagamentoCreate(PagamentoBase):
    pass

class PagamentoUpdate(BaseModel):
    data_pagamento: Optional[date] = None
    valor_pago: Optional[Decimal] = None
    comprovante_url: Optional[str] = None
    observacao: Optional[str] = None

class PagamentoInDB(PagamentoBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True