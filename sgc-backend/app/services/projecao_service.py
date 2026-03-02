# app/services/projecao_service.py
import logging
from datetime import date, timedelta
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.contrato import Contrato
from app.models.boletim_medicao import BoletimMedicao

logger = logging.getLogger(__name__)

def calcular_projecao_contrato(db: Session, contrato_id: int) -> dict:
    """
    Calcula a projeção financeira para um contrato específico.

    Retorna um dicionário com:
        - ritmo_medio_mensal: float
        - saldo_a_executar: float
        - previsao_termino: str (dd/mm/aaaa) ou None
        - faturamento_30d: float
        - faturamento_60d: float
        - faturamento_90d: float
    """
    # Busca o contrato
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise ValueError("Contrato não encontrado")

    valor_total = float(contrato.valor_total) if contrato.valor_total else 0.0

    # Calcula o valor executado (boletins aprovados/faturados)
    valor_executado = db.query(BoletimMedicao).filter(
    BoletimMedicao.contrato_id == contrato_id,
    BoletimMedicao.status.in_(["APROVADO", "FATURADO"])
).with_entities(func.sum(BoletimMedicao.valor_aprovado)).scalar() or 0.0
    valor_executado = float(valor_executado)

    saldo_a_executar = valor_total - valor_executado

    # Busca boletins dos últimos 3 meses
    tres_meses_atras = date.today() - timedelta(days=90)
    boletins_recentes = db.query(BoletimMedicao).filter(
        BoletimMedicao.contrato_id == contrato_id,
        BoletimMedicao.status.in_(["APROVADO", "FATURADO"]),
        BoletimMedicao.periodo_fim >= tres_meses_atras
    ).all()

    # Calcula o ritmo médio mensal
    if boletins_recentes:
        total_recente = sum(float(b.valor_aprovado or 0) for b in boletins_recentes)
        ritmo_medio_mensal = total_recente / len(boletins_recentes)
    else:
        # Fallback: usa o histórico total se houver data de início
        if contrato.data_inicio:
            dias_desde_inicio = (date.today() - contrato.data_inicio).days
            meses_desde_inicio = max(dias_desde_inicio / 30, 1)  # mínimo 1 mês
            ritmo_medio_mensal = valor_executado / meses_desde_inicio
        else:
            ritmo_medio_mensal = 0.0

    # Previsão de término
    previsao_termino: Optional[str] = None
    if ritmo_medio_mensal > 0 and saldo_a_executar > 0:
        meses_restantes = saldo_a_executar / ritmo_medio_mensal
        data_prevista = date.today() + timedelta(days=meses_restantes * 30)
        previsao_termino = data_prevista.strftime("%d/%m/%Y")

    # Projeções de faturamento (mantendo o mesmo ritmo)
    fat_30d = ritmo_medio_mensal * 1
    fat_60d = ritmo_medio_mensal * 2
    fat_90d = ritmo_medio_mensal * 3

    return {
        "ritmo_medio_mensal": round(ritmo_medio_mensal, 2),
        "saldo_a_executar": round(saldo_a_executar, 2),
        "previsao_termino": previsao_termino,
        "faturamento_30d": round(fat_30d, 2),
        "faturamento_60d": round(fat_60d, 2),
        "faturamento_90d": round(fat_90d, 2)
    }


def calcular_projecao_global(db: Session) -> dict:
    """
    Calcula a projeção financeira global (soma de todos os contratos ativos).
    """
    # Filtra contratos com status 'ATIVO'
    contratos = db.query(Contrato).filter(Contrato.status == "ATIVO").all()
    if not contratos:
        return {
            "ritmo_medio_mensal": 0.0,
            "saldo_a_executar": 0.0,
            "previsao_termino": None,
            "faturamento_30d": 0.0,
            "faturamento_60d": 0.0,
            "faturamento_90d": 0.0
        }

    total_saldo = 0.0
    total_ritmo = 0.0
    count = 0

    for contrato in contratos:
        try:
            proj = calcular_projecao_contrato(db, contrato.id)
            total_saldo += proj["saldo_a_executar"]
            total_ritmo += proj["ritmo_medio_mensal"]
            count += 1
        except Exception as e:
            logger.error(f"Erro ao calcular projeção para contrato {contrato.id}: {e}")
            continue

    ritmo_medio_global = total_ritmo / count if count else 0.0
    saldo_global = total_saldo

    previsao_global = None
    if ritmo_medio_global > 0 and saldo_global > 0:
        meses = saldo_global / ritmo_medio_global
        data_prevista = date.today() + timedelta(days=meses * 30)
        previsao_global = data_prevista.strftime("%d/%m/%Y")

    return {
        "ritmo_medio_mensal": round(ritmo_medio_global, 2),
        "saldo_a_executar": round(saldo_global, 2),
        "previsao_termino": previsao_global,
        "faturamento_30d": round(ritmo_medio_global * 1, 2),
        "faturamento_60d": round(ritmo_medio_global * 2, 2),
        "faturamento_90d": round(ritmo_medio_global * 3, 2)
    }