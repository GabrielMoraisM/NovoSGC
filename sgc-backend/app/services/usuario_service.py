from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.usuario_repo import UsuarioRepository
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.core.security import get_password_hash, verify_password

class UsuarioService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UsuarioRepository(db)

    def create_usuario(self, usuario_data: UsuarioCreate):
        # Verifica se e-mail já existe
        if self.repo.get_by_email(usuario_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="E-mail já cadastrado"
            )

        # Cria hash da senha
        hashed = get_password_hash(usuario_data.senha)

        # Prepara dicionário sem a senha em texto plano
        usuario_dict = usuario_data.model_dump(exclude={"senha"})
        usuario_dict["senha_hash"] = hashed

        # Cria o objeto no banco (apenas flush)
        usuario = self.repo.create(**usuario_dict)

        # 🔥 COMMIT para persistir de verdade!
        self.db.commit()

        # Atualiza o objeto com dados do banco (ex: id, created_at)
        self.db.refresh(usuario)

        return usuario

    def get_usuario(self, usuario_id: int):
        usuario = self.repo.get(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return usuario

    def get_usuario_by_email(self, email: str):
        return self.repo.get_by_email(email)

    def update_usuario(self, usuario_id: int, usuario_data: UsuarioUpdate):
        usuario = self.get_usuario(usuario_id)
        update_dict = usuario_data.model_dump(exclude_unset=True)
        if "senha" in update_dict:
            update_dict["senha_hash"] = get_password_hash(update_dict.pop("senha"))
        return self.repo.update(usuario, update_dict)

    def delete_usuario(self, usuario_id: int):
        usuario = self.get_usuario(usuario_id)
        self.repo.delete(usuario.id)