from pydantic import BaseModel, validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

# ----------------------------------------------------------------------
# SCHEMA BASE
# ----------------------------------------------------------------------
class BoletimBase(BaseModel):
    periodo_inicio: date
    periodo_fim: date
    valor_total_medido: Decimal
    valor_glosa: Decimal = 0
    status: str = "RASCUNHO"

    @validator('periodo_fim')
    def valida_periodo(cls, v, values):
        if 'periodo_inicio' in values and v < values['periodo_inicio']:
            raise ValueError('Data fim não pode ser anterior à data início')
        return v

    @validator('valor_total_medido')
    def valida_valor(cls, v):
        if v < 0:
            raise ValueError('Valor total medido não pode ser negativo')
        return v

    @validator('valor_glosa')
    def valida_glosa(cls, v, values):
        if v < 0:
            raise ValueError('Valor de glosa não pode ser negativo')
        if 'valor_total_medido' in values and v > values['valor_total_medido']:
            raise ValueError('Glosa não pode ser maior que o valor total medido')
        return v

    @validator('status')
    def valida_status(cls, v):
        allowed = ('RASCUNHO', 'APROVADO', 'FATURADO', 'CANCELADO')
        if v not in allowed:
            raise ValueError(f'Status deve ser um de {allowed}')
        return v

# ----------------------------------------------------------------------
# SCHEMA PARA CRIAÇÃO (POST)
# ----------------------------------------------------------------------
class BoletimCreate(BoletimBase):
    contrato_id: Optional[int] = None  # ou apenas: contrato_id: int | None = None
    # numero_sequencial NÃO é enviado – é gerado automaticamente pelo listener

# ----------------------------------------------------------------------
# SCHEMA PARA ATUALIZAÇÃO (PUT/PATCH)
# ----------------------------------------------------------------------
class BoletimUpdate(BaseModel):
    periodo_inicio: Optional[date] = None
    periodo_fim: Optional[date] = None
    valor_total_medido: Optional[Decimal] = None
    valor_glosa: Optional[Decimal] = None
    status: Optional[str] = None
    cancelado_motivo: Optional[str] = None

    @validator('periodo_fim')
    def valida_periodo(cls, v, values):
        if v is None:
            return v
        if 'periodo_inicio' in values and values['periodo_inicio'] and v < values['periodo_inicio']:
            raise ValueError('Data fim não pode ser anterior à data início')
        return v

    @validator('valor_total_medido')
    def valida_valor(cls, v):
        if v is not None and v < 0:
            raise ValueError('Valor total medido não pode ser negativo')
        return v

    @validator('valor_glosa')
    def valida_glosa(cls, v, values):
        if v is None:
            return v
        if v < 0:
            raise ValueError('Valor de glosa não pode ser negativo')
        if 'valor_total_medido' in values and values['valor_total_medido'] and v > values['valor_total_medido']:
            raise ValueError('Glosa não pode ser maior que o valor total medido')
        return v

    @validator('status')
    def valida_status(cls, v):
        if v is None:
            return v
        allowed = ('RASCUNHO', 'APROVADO', 'FATURADO', 'CANCELADO')
        if v not in allowed:
            raise ValueError(f'Status deve ser um de {allowed}')
        return v

# ----------------------------------------------------------------------
# SCHEMA PARA RESPOSTA (GET)
# ----------------------------------------------------------------------
class BoletimInDB(BoletimBase):
    id: int
    contrato_id: int
    numero_sequencial: int
    valor_aprovado: Optional[Decimal]
    cancelado_motivo: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True