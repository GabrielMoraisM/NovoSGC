from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Dict, Any
from datetime import date, timedelta
from app.api.deps import get_db, get_current_user
from app.models.boletim_medicao import BoletimMedicao
from app.models.faturamento import Faturamento
from app.models.pagamento import Pagamento
from app.models.contrato import Contrato

router = APIRouter()

@router.get("/evolucao-contrato/{contrato_id}")
def get_evolucao_contrato(
    contrato_id: int,
    meses: int = Query(12, description="Número de meses para retornar"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retorna dados de evolução mensal para o gráfico.
    """
    # Buscar contrato para datas
    contrato = db.get(Contrato, contrato_id)
    if not contrato:
        return {"error": "Contrato não encontrado"}
    
    # Gerar lista dos últimos N meses
    hoje = date.today()
    labels = []
    fisico_mensal = []
    financeiro_mensal = []
    tempo_mensal = []
    
    for i in range(meses-1, -1, -1):
        mes_ano = hoje - timedelta(days=30*i)
        mes = mes_ano.month
        ano = mes_ano.year
        
        labels.append(f"{mes:02d}/{ano}")
        
        # % Físico acumulado até este mês
        fisico = db.query(func.sum(BoletimMedicao.valor_aprovado)).filter(
            BoletimMedicao.contrato_id == contrato_id,
            BoletimMedicao.status.in_(["APROVADO", "FATURADO"]),
            extract('year', BoletimMedicao.periodo_fim) <= ano,
            extract('month', BoletimMedicao.periodo_fim) <= mes
        ).scalar() or 0
        
        perc_fisico = (fisico / contrato.valor_total * 100) if contrato.valor_total else 0
        fisico_mensal.append(round(perc_fisico, 2))
        
        # % Financeiro acumulado até este mês
        financeiro = db.query(func.sum(Pagamento.valor_pago)).join(
            Faturamento, Faturamento.id == Pagamento.faturamento_id
        ).join(
            BoletimMedicao, BoletimMedicao.id == Faturamento.bm_id
        ).filter(
            BoletimMedicao.contrato_id == contrato_id,
            extract('year', Pagamento.data_pagamento) <= ano,
            extract('month', Pagamento.data_pagamento) <= mes
        ).scalar() or 0
        
        perc_financeiro = (financeiro / contrato.valor_total * 100) if contrato.valor_total else 0
        financeiro_mensal.append(round(perc_financeiro, 2))
        
        # % Tempo decorrido
        if contrato.data_inicio and contrato.data_fim_prevista:
            dias_totais = (contrato.data_fim_prevista - contrato.data_inicio).days
            data_limite = date(ano, mes, 1).replace(day=28)  # aproximação
            dias_decorridos = (data_limite - contrato.data_inicio).days
            perc_tempo = max(0, min(100, (dias_decorridos / dias_totais * 100)))
            tempo_mensal.append(round(perc_tempo, 2))
        else:
            tempo_mensal.append(0)
    
    return {
        "labels": labels,
        "fisico": fisico_mensal,
        "financeiro": financeiro_mensal,
        "tempo": tempo_mensal
    }

@router.get("/evolucao-global")
def get_evolucao_global(
    meses: int = Query(12, description="Número de meses para retornar"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retorna dados de evolução global (todos os contratos ativos).
    """
    contratos = db.query(Contrato).filter(Contrato.status == "ATIVO").all()
    if not contratos:
        return {"labels": [], "fisico": [], "financeiro": [], "tempo": []}
    
    valor_total_geral = sum((c.valor_total or 0) for c in contratos)
    
    hoje = date.today()
    labels = []
    fisico_mensal = []
    financeiro_mensal = []
    
    for i in range(meses-1, -1, -1):
        mes_ano = hoje - timedelta(days=30*i)
        mes = mes_ano.month
        ano = mes_ano.year
        labels.append(f"{mes:02d}/{ano}")
        
        # Soma física de todos contratos
        fisico = 0
        financeiro = 0
        for c in contratos:
            # Físico
            fisico += db.query(func.sum(BoletimMedicao.valor_aprovado)).filter(
                BoletimMedicao.contrato_id == c.id,
                BoletimMedicao.status.in_(["APROVADO", "FATURADO"]),
                extract('year', BoletimMedicao.periodo_fim) <= ano,
                extract('month', BoletimMedicao.periodo_fim) <= mes
            ).scalar() or 0
            
            # Financeiro
            financeiro += db.query(func.sum(Pagamento.valor_pago)).join(
                Faturamento, Faturamento.id == Pagamento.faturamento_id
            ).join(
                BoletimMedicao, BoletimMedicao.id == Faturamento.bm_id
            ).filter(
                BoletimMedicao.contrato_id == c.id,
                extract('year', Pagamento.data_pagamento) <= ano,
                extract('month', Pagamento.data_pagamento) <= mes
            ).scalar() or 0
        
        perc_fisico = (fisico / valor_total_geral * 100) if valor_total_geral else 0
        perc_financeiro = (financeiro / valor_total_geral * 100) if valor_total_geral else 0
        
        fisico_mensal.append(round(perc_fisico, 2))
        financeiro_mensal.append(round(perc_financeiro, 2))
    
    return {
        "labels": labels,
        "fisico": fisico_mensal,
        "financeiro": financeiro_mensal
    }