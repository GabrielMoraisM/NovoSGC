from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.arquivo import Arquivo
from app.repositories.base import BaseRepository


class ArquivoRepository(BaseRepository[Arquivo]):
    def __init__(self, db: Session):
        super().__init__(db, Arquivo)

    def get_by_entidade(self, entidade_tipo: str, entidade_id: int) -> List[Arquivo]:
        return (
            self.db.query(Arquivo)
            .filter(
                Arquivo.entidade_tipo == entidade_tipo,
                Arquivo.entidade_id == entidade_id,
            )
            .order_by(Arquivo.created_at.asc())
            .all()
        )

    def list_all(self, entidade_tipo: Optional[str] = None, entidade_id: Optional[int] = None) -> List[Arquivo]:
        query = self.db.query(Arquivo)
        if entidade_tipo:
            query = query.filter(Arquivo.entidade_tipo == entidade_tipo)
        if entidade_id is not None:
            query = query.filter(Arquivo.entidade_id == entidade_id)
        return query.order_by(Arquivo.created_at.desc()).all()
