from typing import List
from pydantic import BaseModel
from app.schemas.faturamento import FaturamentoInDB

class RateioResponse(BaseModel):
    boletim_id: int
    contrato_id: int
    participantes_rateados: int
    faturas_geradas: List[FaturamentoInDB]