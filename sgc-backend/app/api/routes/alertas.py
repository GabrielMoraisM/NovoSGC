from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, timedelta
from app.api.deps import get_db, get_current_user
from app.models.contrato import Contrato
from app.models.boletim_medicao import BoletimMedicao
from app.models.faturamento import Faturamento
from app.models.contrato_seguro import ContratoSeguro
from app.services import financeiro_service

router = APIRouter()

@router.get("/")
def listar_alertas(
    contrato_id: Optional[int] = Query(None, description="Filtrar alertas por contrato"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lista alertas reais baseados em regras de negócio."""
    alertas = []
    
    # Base de contratos para filtrar
    query_contratos = db.query(Contrato)
    if contrato_id:
        query_contratos = query_contratos.filter(Contrato.id == contrato_id)
    contratos = query_contratos.all()
    
    for c in contratos:
        # 1. Alerta de atraso crítico (desempenho)
        try:
            resumo = financeiro_service.calcular_resumo_contrato(db, c.id)
            desempenho = financeiro_service.calcular_status_desempenho(db, c.id)
            
            if desempenho["status_desempenho"] == "ATRASADO":
                alertas.append({
                    "id": f"atraso_{c.id}",
                    "tipo": "danger",
                    "titulo": "Contrato em atraso",
                    "mensagem": f"{c.numero_contrato} está com execução abaixo do cronograma",
                    "data": date.today().isoformat(),
                    "contrato_id": c.id
                })
        except:
            pass
        
        # 2. Alerta de seguros a vencer (próximos 30 dias)
        seguros = db.query(ContratoSeguro).filter(
            ContratoSeguro.contrato_id == c.id,
            ContratoSeguro.data_fim <= date.today() + timedelta(days=30),
            ContratoSeguro.data_fim >= date.today()
        ).all()
        
        for s in seguros:
            alertas.append({
                "id": f"seguro_{s.id}",
                "tipo": "warning",
                "titulo": "Seguro a vencer",
                "mensagem": f"Seguro {s.tipo} vence em {s.data_fim.strftime('%d/%m/%Y')}",
                "data": date.today().isoformat(),
                "contrato_id": c.id
            })
        
        # 3. Alerta de faturamento pendente (BMs aprovados sem NF)
        bms_sem_fatura = db.query(BoletimMedicao).filter(
            BoletimMedicao.contrato_id == c.id,
            BoletimMedicao.status == "APROVADO"
        ).count()
        
        if bms_sem_fatura > 0:
            alertas.append({
                "id": f"fatura_{c.id}",
                "tipo": "info",
                "titulo": "Medições a faturar",
                "mensagem": f"{bms_sem_fatura} boletim(ns) aprovado(s) aguardando emissão de NF",
                "data": date.today().isoformat(),
                "contrato_id": c.id
            })
        
        # 4. Alerta de desequilíbrio físico-financeiro
        try:
            if resumo["percentual_fisico"] - resumo["percentual_financeiro"] > 15:
                alertas.append({
                    "id": f"desequilibrio_{c.id}",
                    "tipo": "warning",
                    "titulo": "Desequilíbrio financeiro",
                    "mensagem": f"Executado {resumo['percentual_fisico']:.1f}% x Recebido {resumo['percentual_financeiro']:.1f}%",
                    "data": date.today().isoformat(),
                    "contrato_id": c.id
                })
        except:
            pass
    
    return alertas