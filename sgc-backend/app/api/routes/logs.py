from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.api import deps
from app.services.log_service import LogService
from app.schemas.log import LogResponse  # vamos criar esse schema

router = APIRouter()

@router.get("/", response_model=list[LogResponse])
def listar_logs(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
    usuario_id: Optional[int] = Query(None),
    entidade: Optional[str] = Query(None),
    acao: Optional[str] = Query(None),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500)
):
    # Opcional: restringir acesso a administradores/TI
    if current_user.perfil not in ["ADMIN", "TI"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Acesso negado")
    service = LogService(db)
    return service.listar_logs(
        usuario_id=usuario_id,
        entidade=entidade,
        acao=acao,
        data_inicio=data_inicio,
        data_fim=data_fim,
        skip=skip,
        limit=limit
    )