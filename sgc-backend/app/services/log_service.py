from sqlalchemy.orm import Session
from app.repositories.log_repository import LogRepository
from typing import Optional, Dict, Any
from datetime import date

class LogService:
    def __init__(self, db: Session):
        self.repo = LogRepository(db)

    def registrar_log(
        self,
        usuario_id: Optional[int],
        usuario_email: Optional[str],
        acao: str,
        entidade: str,
        entidade_id: Optional[int] = None,
        dados_antigos: Optional[Dict[str, Any]] = None,
        dados_novos: Optional[Dict[str, Any]] = None,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        return self.repo.create(
            usuario_id=usuario_id,
            usuario_email=usuario_email,
            acao=acao,
            entidade=entidade,
            entidade_id=entidade_id,
            dados_antigos=dados_antigos,
            dados_novos=dados_novos,
            ip=ip,
            user_agent=user_agent
        )

    def listar_logs(self, **filtros):
        return self.repo.list(**filtros)