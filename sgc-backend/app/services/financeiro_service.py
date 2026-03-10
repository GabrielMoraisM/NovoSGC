# app/services/financeiro_service.py
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import date
from typing import Dict, Any

from app.models.boletim_medicao import BoletimMedicao
from app.models.faturamento import Faturamento
from app.models.pagamento import Pagamento
from app.models.contrato import Contrato
from app.models.aditivo import Aditivo
from app.core.exceptions import BusinessError

def calcular_resumo_contrato(db: Session, contrato_id: int) -> Dict[str, Any]:
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise BusinessError("Contrato não encontrado.")

    valor_total = float(contrato.valor_total) if contrato.valor_total else 0.0

    # Valor executado (boletins APROVADOS e FATURADOS — ambos representam execução confirmada)
    valor_executado = db.query(func.sum(BoletimMedicao.valor_aprovado)).filter(
        BoletimMedicao.contrato_id == contrato_id,
        BoletimMedicao.status.in_(["APROVADO", "FATURADO"])
    ).scalar() or 0.0
    valor_executado = float(valor_executado)

    # Valor faturado (soma das notas fiscais não canceladas)
    valor_faturado = db.query(func.sum(Faturamento.valor_bruto_nf)).join(
        BoletimMedicao, BoletimMedicao.id == Faturamento.bm_id
    ).filter(
        BoletimMedicao.contrato_id == contrato_id,
        Faturamento.status != "CANCELADO"
    ).scalar() or 0.0
    valor_faturado = float(valor_faturado)

    # Valor recebido (soma dos pagamentos de faturas não canceladas)
    valor_recebido = db.query(func.sum(Pagamento.valor_pago)).join(
        Faturamento, Faturamento.id == Pagamento.faturamento_id
    ).join(
        BoletimMedicao, BoletimMedicao.id == Faturamento.bm_id
    ).filter(
        BoletimMedicao.contrato_id == contrato_id,
        Faturamento.status != "CANCELADO"
    ).scalar() or 0.0
    valor_recebido = float(valor_recebido)

    saldo_contratual = valor_total - valor_executado
    saldo_a_faturar = valor_executado - valor_faturado
    saldo_a_receber = valor_faturado - valor_recebido

    if valor_total:
        perc_fisico = (valor_executado / valor_total) * 100
        perc_financeiro_faturado = (valor_faturado / valor_total) * 100   # baseado no faturado
        perc_financeiro_recebido = (valor_recebido / valor_total) * 100   # baseado no recebido
    else:
        perc_fisico = perc_financeiro_faturado = perc_financeiro_recebido = 0.0

    return {
        "valor_total_contrato": round(valor_total, 2),
        "valor_executado": round(valor_executado, 2),
        "valor_faturado": round(valor_faturado, 2),
        "valor_recebido": round(valor_recebido, 2),
        "saldo_contratual": round(saldo_contratual, 2),
        "saldo_a_faturar": round(saldo_a_faturar, 2),
        "saldo_a_receber": round(saldo_a_receber, 2),
        "percentual_fisico": round(perc_fisico, 2),
        "percentual_financeiro_faturado": round(perc_financeiro_faturado, 2),
        "percentual_financeiro_recebido": round(perc_financeiro_recebido, 2),
        "percentual_financeiro": round(perc_financeiro_faturado, 2),  # compatibilidade com frontend
    }

def calcular_status_desempenho(db: Session, contrato_id: int) -> Dict[str, Any]:
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise BusinessError("Contrato não encontrado.")

    hoje = date.today()
    data_inicio = contrato.data_inicio
    data_fim = contrato.data_fim_prevista

    if not data_inicio or not data_fim:
        return {
            "percentual_tempo": None,
            "status_desempenho": "SEM_PRAZO",
            "dias_decorridos": None,
            "dias_totais": None,
        }

    # Soma os dias de aditivos de prazo (tipo PRAZO ou AMBOS)
    dias_aditivos = db.query(func.sum(Aditivo.dias_acrescimo)).filter(
        Aditivo.contrato_id == contrato_id,
        Aditivo.tipo.in_(["PRAZO", "AMBOS"])
    ).scalar() or 0

    dias_totais = (data_fim - data_inicio).days + dias_aditivos
    dias_decorridos = (hoje - data_inicio).days

    if dias_totais <= 0:
        percentual_tempo = 0.0
    else:
        percentual_tempo = min(100.0, max(0.0, (dias_decorridos / dias_totais) * 100))

    resumo = calcular_resumo_contrato(db, contrato_id)
    perc_fisico = resumo["percentual_fisico"]

    if perc_fisico is None:
        status = "SEM_MEDICAO"
    elif percentual_tempo > perc_fisico + 10:
        status = "ATRASADO"
    elif perc_fisico > percentual_tempo + 10:
        status = "ADIANTADO"
    else:
        status = "EM_DIA"

    return {
        "percentual_tempo": round(percentual_tempo, 2),
        "status_desempenho": status,
        "dias_decorridos": dias_decorridos,
        "dias_totais": dias_totais,
    }