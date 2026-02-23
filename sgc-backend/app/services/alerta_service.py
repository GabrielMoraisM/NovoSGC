from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List, Dict, Any
from app.models.contrato import Contrato
from app.models.contrato_seguro import ContratoSeguro
from app.models.boletim_medicao import BoletimMedicao, StatusBM
from app.services import financeiro_service

def gerar_alertas_contrato(db: Session, contrato_id: int) -> List[Dict[str, Any]]:
    alertas = []
    contrato = db.get(Contrato, contrato_id)
    if not contrato:
        return alertas

    hoje = date.today()

    # 1. Alerta de prazo próximo do fim (ex: 30 dias)
    if contrato.data_fim:
        dias_restantes = (contrato.data_fim - hoje).days
        if 0 <= dias_restantes <= 30:
            alertas.append({
                "tipo": "PRAZO",
                "severidade": "ALTA" if dias_restantes <= 7 else "MEDIA",
                "mensagem": f"Contrato termina em {dias_restantes} dias ({contrato.data_fim.strftime('%d/%m/%Y')})",
                "data_referencia": contrato.data_fim
            })

    # 2. Alerta de seguros a vencer
    seguros = db.query(ContratoSeguro).filter(
        ContratoSeguro.contrato_id == contrato_id,
        ContratoSeguro.data_fim_vigencia >= hoje,
        ContratoSeguro.data_fim_vigencia <= hoje + timedelta(days=30)
    ).all()
    for seguro in seguros:
        dias = (seguro.data_fim_vigencia - hoje).days
        alertas.append({
            "tipo": "SEGURO",
            "severidade": "ALTA" if dias <= 7 else "MEDIA",
            "mensagem": f"Seguro {seguro.tipo_seguro} vence em {dias} dias",
            "data_referencia": seguro.data_fim_vigencia
        })

    # 3. Alerta de desequilíbrio físico x financeiro (já temos no serviço de desempenho)
    desempenho = financeiro_service.calcular_status_desempenho(db, contrato_id)
    if desempenho["status_desempenho"] == "ATRASADO":
        alertas.append({
            "tipo": "DESEMPENHO",
            "severidade": "ALTA",
            "mensagem": "Contrato atrasado: progresso físico menor que o esperado para o tempo decorrido",
            "data_referencia": hoje
        })

    return alertas