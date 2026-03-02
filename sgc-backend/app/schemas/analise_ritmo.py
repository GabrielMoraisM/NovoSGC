from pydantic import BaseModel
from typing import Optional

class AnaliseRitmoResponse(BaseModel):
    valor_total_contrato: float
    dias_totais: int
    dias_decorridos: int
    valor_executado: float
    percentual_fisico: float
    valor_planejado_acumulado: float
    ritmo_planejado_diario: float
    ritmo_real_medio: Optional[float]
    desvio_valor: float
    desvio_percentual: Optional[float]
    ritmo_necessario_para_recuperar: Optional[float]
    status: str  # "ADIANTADO", "ATRASADO", "NO_PRAZO"