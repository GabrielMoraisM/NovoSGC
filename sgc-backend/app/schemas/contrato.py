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
    valor_total: Optional[Decimal]          # Valor atualizado com aditivos
    numero_os: Optional[str]
    data_os: Optional[date]
    descricao_os: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    gestor: Optional[str] = None

    # Campos do relacionamento (opcionais, preenchidos via join)
    cliente_nome: Optional[str] = None

    # Campos calculados para resumo financeiro e de desempenho (opcionais)
    # Esses campos são preenchidos apenas quando solicitado (?incluir_resumo=true)
    valor_executado: Optional[float] = None      # Soma dos BMs aprovados/faturados
    valor_faturado: Optional[float] = None       # Soma das NFs não canceladas
    valor_recebido: Optional[float] = None       # Soma dos pagamentos
    percentual_fisico: Optional[float] = None    # (valor_executado / valor_total) * 100
    percentual_financeiro: Optional[float] = None # (valor_recebido / valor_total) * 100
    saldo_contratual: Optional[float] = None     # valor_total - valor_executado
    saldo_a_faturar: Optional[float] = None      # valor_executado - valor_faturado
    saldo_a_receber: Optional[float] = None      # valor_faturado - valor_recebido

    # Campos de desempenho temporal
    percentual_tempo: Optional[float] = None     # dias_decorridos / dias_totais * 100
    status_desempenho: Optional[str] = None      # EM_DIA, ATRASADO, ADIANTADO, SEM_PRAZO, SEM_MEDICAO
    dias_decorridos: Optional[int] = None        # dias desde data_inicio até hoje
    dias_totais: Optional[int] = None            # prazo original (ou atualizado via aditivos)

    class Config:
        from_attributes = True