from pydantic import BaseModel, validator
from typing import List, Optional
from decimal import Decimal

# ----------------------------------------------------------------------
# SCHEMA BASE – representa um único participante
# ----------------------------------------------------------------------
class ParticipanteBase(BaseModel):
    empresa_id: int
    percentual_participacao: Decimal
    is_lider: bool = False

    @validator('percentual_participacao')
    def valida_percentual(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Percentual deve estar entre 0 e 100')
        return v

# ----------------------------------------------------------------------
# SCHEMA PARA CRIAÇÃO/ATUALIZAÇÃO (usado na lista)
# ----------------------------------------------------------------------
class ParticipanteCreate(ParticipanteBase):
    pass

# ----------------------------------------------------------------------
# SCHEMA PARA RESPOSTA (inclui contrato_id e empresa)
# ----------------------------------------------------------------------
class ParticipanteInDB(ParticipanteBase):
    contrato_id: int
    empresa_id: int
    empresa_nome: Optional[str] = None  # para facilitar no front

    class Config:
        from_attributes = True

# ----------------------------------------------------------------------
# SCHEMA PARA SUBSTITUIÇÃO COMPLETA DA LISTA
# ----------------------------------------------------------------------
class ParticipanteList(BaseModel):
    participantes: List[ParticipanteCreate]

    @validator('participantes')
    def valida_soma_percentual(cls, v):
        total = sum(p.percentual_participacao for p in v)
        if total != Decimal('100.00'):
            raise ValueError(f'A soma dos percentuais deve ser 100% (atual: {total}%)')
        # Verificar se há exatamente um líder (opcional, mas recomendado)
        lideres = [p for p in v if p.is_lider]
        if len(lideres) != 1:
            raise ValueError('Deve haver exatamente um líder no consórcio')
        return v