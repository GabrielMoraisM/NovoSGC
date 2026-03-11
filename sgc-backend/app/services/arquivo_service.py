import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.models.arquivo import Arquivo
from app.repositories.arquivo_repository import ArquivoRepository

# Upload directory — stored inside sgc-backend/uploads/
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # sgc-backend/
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".gif",
    ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".txt", ".zip"
}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


class ArquivoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ArquivoRepository(db)

    def upload_arquivo(
        self,
        file: UploadFile,
        entidade_tipo: str,
        entidade_id: int,
        descricao: Optional[str],
        usuario_id: Optional[int],
    ) -> Arquivo:
        # Validate extension
        original_name = file.filename or "arquivo"
        suffix = Path(original_name).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Tipo de arquivo não permitido: {suffix}. Permitidos: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            )

        # Read content and check size
        content = file.file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Arquivo muito grande. Tamanho máximo: 50 MB.",
            )

        # Generate unique filename
        unique_name = f"{uuid.uuid4().hex}{suffix}"
        file_path = UPLOAD_DIR / unique_name

        # Save to disk
        file_path.write_bytes(content)

        # Save to DB
        arquivo = Arquivo(
            nome_original=original_name,
            nome_arquivo=unique_name,
            caminho=str(file_path),
            tamanho=len(content),
            tipo_mime=file.content_type,
            entidade_tipo=entidade_tipo,
            entidade_id=entidade_id,
            descricao=descricao,
            usuario_id=usuario_id,
        )
        self.db.add(arquivo)
        self.db.commit()
        self.db.refresh(arquivo)
        return arquivo

    def get_arquivo(self, arquivo_id: int) -> Arquivo:
        arquivo = self.repo.get(arquivo_id)
        if not arquivo:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
        return arquivo

    def delete_arquivo(self, arquivo_id: int) -> None:
        arquivo = self.get_arquivo(arquivo_id)
        # Remove from disk
        path = Path(arquivo.caminho)
        if path.exists():
            path.unlink()
        self.db.delete(arquivo)
        self.db.commit()

    def get_by_entidade(self, entidade_tipo: str, entidade_id: int) -> List[Arquivo]:
        return self.repo.get_by_entidade(entidade_tipo, entidade_id)

    def list_all(self, entidade_tipo: Optional[str] = None, entidade_id: Optional[int] = None) -> List[Arquivo]:
        return self.repo.list_all(entidade_tipo, entidade_id)
