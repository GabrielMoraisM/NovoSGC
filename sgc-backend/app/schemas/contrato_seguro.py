from pydantic import BaseModel, validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

class ContratoSeguroBase(BaseModel):
    seguradora_id: int
    tipo: str  # 'GARANTIA_CONTRATUAL', 'RISCO_ENGENHARIA', 'RC'
    numero_apolice: str
    data_vencimento: date
    valor: Decimal
    objeto: Optional[str] = None  # descrição do que está sendo segurado

    @validator('tipo')
    def valida_tipo(cls, v):
        allowed = ('GARANTIA_CONTRATUAL', 'RISCO_ENGENHARIA', 'RC')
        if v not in allowed:
            raise ValueError(f'Tipo deve ser um de {allowed}')
        return v

class ContratoSeguroCreate(ContratoSeguroBase):
    pass

class ContratoSeguroUpdate(BaseModel):
    seguradora_id: Optional[int] = None
    tipo: Optional[str] = None
    numero_apolice: Optional[str] = None
    data_vencimento: Optional[date] = None
    valor: Optional[Decimal] = None
    objeto: Optional[str] = None

    @validator('tipo')
    def valida_tipo(cls, v):
        if v is None:
            return v
        allowed = ('GARANTIA_CONTRATUAL', 'RISCO_ENGENHARIA', 'RC')
        if v not in allowed:
            raise ValueError(f'Tipo deve ser um de {allowed}')
        return v

class ContratoSeguroInDB(ContratoSeguroBase):
    id: int
    contrato_id: int
    created_at: datetime

    class Config:
        from_attributes = True