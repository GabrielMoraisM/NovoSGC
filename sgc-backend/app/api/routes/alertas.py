from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.deps import get_db, get_current_user
from app.services.alerta_service import AlertaService

router = APIRouter()

@router.get("/")
def listar_alertas(
    contrato_id: Optional[int] = Query(None, description="Filtrar por contrato"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = AlertaService(db)
    alertas = service.gerar_alertas(contrato_id)
    return alertas