from pydantic import BaseModel, validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

# ----------------------------------------------------------------------
# SCHEMA BASE (atributos comuns)
# ----------------------------------------------------------------------
class ContratoBase(BaseModel):
    numero_contrato: str
    tipo_obra: str  # 'HECA_100', 'CONSORCIO', 'SCP'
    valor_original: Decimal
    prazo_original_dias: int
    data_inicio: date
    cliente_id: int
    iss_percentual_padrao: Optional[Decimal] = None
    status: Optional[str] = "ATIVO"


    @validator('tipo_obra')
    def valida_tipo_obra(cls, v):
        allowed = ('HECA_100', 'CONSORCIO', 'SCP')
        if v not in allowed:
            raise ValueError(f'Tipo de obra deve ser um de {allowed}')
        return v

    @validator('status')
    def valida_status(cls, v):
        allowed = ('ATIVO', 'PARALISADO', 'ENCERRADO')
        if v not in allowed:
            raise ValueError(f'Status deve ser um de {allowed}')
        return v

# ----------------------------------------------------------------------
# SCHEMA PARA CRIAÇÃO (POST)
# ----------------------------------------------------------------------
class ContratoCreate(ContratoBase):
    pass

# ----------------------------------------------------------------------
# SCHEMA PARA ATUALIZAÇÃO (PUT/PATCH)
# ----------------------------------------------------------------------
class ContratoUpdate(BaseModel):
    numero_contrato: Optional[str] = None
    tipo_obra: Optional[str] = None
    valor_original: Optional[Decimal] = None
    prazo_original_dias: Optional[int] = None
    data_inicio: Optional[date] = None
    cliente_id: Optional[int] = None
    iss_percentual_padrao: Optional[Decimal] = None
    status: Optional[str] = None
    numero_os: Optional[str] = None
    data_os: Optional[date] = None
    descricao_os: Optional[str] = None
    gestor: Optional[str] = None  

    @validator('tipo_obra')
    def valida_tipo_obra(cls, v):
        if v is None:
            return v
        allowed = ('HECA_100', 'CONSORCIO', 'SCP')
        if v not in allowed:
            raise ValueError(f'Tipo de obra deve ser um de {allowed}')
        return v

    @validator('status')
    def valida_status(cls, v):
        if v is None:
            return v
        allowed = ('ATIVO', 'PARALISADO', 'ENCERRADO')
        if v not in allowed:
            raise ValueError(f'Status deve ser um de {allowed}')
        return v

# ----------------------------------------------------------------------
# SCHEMA PARA RESPOSTA (GET)
# ----------------------------------------------------------------------
class ContratoInDB(ContratoBase):
    id: int
    data_fim_prevista: Optional[date]
    valor_total: Optional[Decimal]
    numero_os: Optional[str]          # <-- adicione
    data_os: Optional[date]           # <-- adicione
    descricao_os: Optional[str]       # <-- adicione
    created_at: datetime
    updated_at: Optional[datetime]
    gestor: Optional[str] = None


    class Config:
        from_attributes = True