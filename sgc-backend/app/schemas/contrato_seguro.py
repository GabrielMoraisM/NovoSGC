from pydantic import BaseModel, validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

class ContratoSeguroBase(BaseModel):
    seguradora_id: int
    numero_apolice: str
    tipo: str
    valor: Decimal
    data_vencimento: date
    cliente_id: int
    tomador_id: int
    objeto_segurado: str
    possui_clausula_retomada: Optional[bool] = False
    observacoes: Optional[str] = None

    @validator('tipo')
    def valida_tipo(cls, v):
        valores_aceitos = {
            'LICITACAO', 'CONTRATO', 'RESPONSABILIDADE_CIVIL',
            'RISCO_PROFISSIONAL', 'RISCO_ENGENHARIA', 'GARANTIA_CONTRATUAL_RETOMADA'
        }
        if v not in valores_aceitos:
            raise ValueError(f'Tipo inválido. Valores aceitos: {", ".join(sorted(valores_aceitos))}')
        return v

class ContratoSeguroCreate(ContratoSeguroBase):
    pass

class ContratoSeguroUpdate(BaseModel):
    seguradora_id: Optional[int] = None
    numero_apolice: Optional[str] = None
    tipo: Optional[str] = None
    valor: Optional[Decimal] = None
    data_vencimento: Optional[date] = None
    cliente_id: Optional[int] = None
    tomador_id: Optional[int] = None
    objeto_segurado: Optional[str] = None
    possui_clausula_retomada: Optional[bool] = None
    observacoes: Optional[str] = None

    @validator('tipo')
    def valida_tipo(cls, v):
        if v is None:
            return v
        valores_aceitos = {
            'LICITACAO', 'CONTRATO', 'RESPONSABILIDADE_CIVIL',
            'RISCO_PROFISSIONAL', 'RISCO_ENGENHARIA', 'GARANTIA_CONTRATUAL_RETOMADA'
        }
        if v not in valores_aceitos:
            raise ValueError(f'Tipo inválido. Valores aceitos: {", ".join(sorted(valores_aceitos))}')
        return v

class ContratoSeguroInDB(ContratoSeguroBase):
    id: int
    contrato_id: int
    created_at: datetime

    class Config:
        from_attributes = True