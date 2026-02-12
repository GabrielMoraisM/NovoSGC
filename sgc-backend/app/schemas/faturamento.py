from pydantic import BaseModel, validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

# ----------------------------------------------------------------------
# SCHEMA BASE
# ----------------------------------------------------------------------
class FaturamentoBase(BaseModel):
    bm_id: int
    numero_nf: Optional[str] = None
    empresa_emissora_id: int
    cliente_id: int
    valor_bruto_nf: Decimal
    data_emissao: date
    data_vencimento: date
    status: str = "PENDENTE"

    @validator('data_vencimento')
    def valida_vencimento(cls, v, values):
        if 'data_emissao' in values and v < values['data_emissao']:
            raise ValueError('Data de vencimento não pode ser anterior à data de emissão')
        return v

    @validator('valor_bruto_nf')
    def valida_valor(cls, v):
        if v <= 0:
            raise ValueError('Valor bruto deve ser maior que zero')
        return v

    @validator('status')
    def valida_status(cls, v):
        allowed = ('PENDENTE', 'PARCIAL', 'QUITADO', 'CANCELADO', 'VENCIDO')
        if v not in allowed:
            raise ValueError(f'Status deve ser um de {allowed}')
        return v

# ----------------------------------------------------------------------
# SCHEMA PARA CRIAÇÃO (POST)
# ----------------------------------------------------------------------
class FaturamentoCreate(FaturamentoBase):
    pass  # todos os campos obrigatórios

# ----------------------------------------------------------------------
# SCHEMA PARA ATUALIZAÇÃO (PUT/PATCH)
# ----------------------------------------------------------------------
class FaturamentoUpdate(BaseModel):
    numero_nf: Optional[str] = None
    empresa_emissora_id: Optional[int] = None
    cliente_id: Optional[int] = None
    valor_bruto_nf: Optional[Decimal] = None
    data_emissao: Optional[date] = None
    data_vencimento: Optional[date] = None
    status: Optional[str] = None

    @validator('data_vencimento')
    def valida_vencimento(cls, v, values):
        if v is None:
            return v
        if 'data_emissao' in values and values['data_emissao'] and v < values['data_emissao']:
            raise ValueError('Data de vencimento não pode ser anterior à data de emissão')
        return v

    @validator('status')
    def valida_status(cls, v):
        if v is None:
            return v
        allowed = ('PENDENTE', 'PARCIAL', 'QUITADO', 'CANCELADO', 'VENCIDO')
        if v not in allowed:
            raise ValueError(f'Status deve ser um de {allowed}')
        return v

# ----------------------------------------------------------------------
# SCHEMA PARA RESPOSTA (GET)
# ----------------------------------------------------------------------
class FaturamentoInDB(FaturamentoBase):
    id: int
    valor_liquido_nf: Decimal
    iss_retido: Decimal
    inss_retido: Decimal
    irrf_retido: Decimal
    csll_retido: Decimal
    pis_retido: Decimal
    cofins_retido: Decimal
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True