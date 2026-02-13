from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.art_repo import ArtRepository
from app.repositories.contrato_repo import ContratoRepository
from app.schemas.art import ArtCreate, ArtUpdate
from app.models.contrato_art import ContratoArt

class ArtService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ArtRepository(db)
        self.contrato_repo = ContratoRepository(db)

    def create_art(self, contrato_id: int, art_data: ArtCreate) -> ContratoArt:
        # Verificar se contrato existe
        contrato = self.contrato_repo.get(contrato_id)
        if not contrato:
            raise HTTPException(status_code=404, detail="Contrato não encontrado")
        art_dict = art_data.model_dump()
        art_dict['contrato_id'] = contrato_id
        art = self.repo.create(**art_dict)
        self.db.commit()
        self.db.refresh(art)
        return art

    def get_arts_por_contrato(self, contrato_id: int) -> list[ContratoArt]:
        # Verificar se contrato existe (opcional, mas bom)
        contrato = self.contrato_repo.get(contrato_id)
        if not contrato:
            raise HTTPException(status_code=404, detail="Contrato não encontrado")
        return self.repo.get_by_contrato(contrato_id)

    def get_art(self, art_id: int) -> ContratoArt:
        art = self.repo.get(art_id)
        if not art:
            raise HTTPException(status_code=404, detail="ART não encontrada")
        return art

    def update_art(self, art_id: int, art_data: ArtUpdate) -> ContratoArt:
        art = self.get_art(art_id)
        update_dict = art_data.model_dump(exclude_unset=True)
        art_atualizado = self.repo.update(art, update_dict)
        self.db.commit()
        self.db.refresh(art_atualizado)
        return art_atualizado

    def delete_art(self, art_id: int) -> None:
        art = self.get_art(art_id)
        self.repo.delete(art.id)
        self.db.commit()