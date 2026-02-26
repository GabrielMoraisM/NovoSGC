from sqlalchemy.orm import Session
from app.models.log import Log
from typing import Optional, List
from datetime import date

class LogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> Log:
        log = Log(**kwargs)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def list(self, usuario_id: Optional[int] = None, entidade: Optional[str] = None,
             acao: Optional[str] = None, data_inicio: Optional[date] = None,
             data_fim: Optional[date] = None, skip: int = 0, limit: int = 100) -> List[Log]:
        query = self.db.query(Log)
        if usuario_id:
            query = query.filter(Log.usuario_id == usuario_id)
        if entidade:
            query = query.filter(Log.entidade == entidade)
        if acao:
            query = query.filter(Log.acao == acao)
        if data_inicio:
            query = query.filter(Log.created_at >= data_inicio)
        if data_fim:
            query = query.filter(Log.created_at <= data_fim)
        return query.order_by(Log.created_at.desc()).offset(skip).limit(limit).all()