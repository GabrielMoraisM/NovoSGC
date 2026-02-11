# app/services/usuario_service.py
from sqlalchemy.orm import Session
from app.repositories.usuario_repo import UsuarioRepository
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.core.security import get_password_hash, verify_password
from app.models.usuario import Usuario

class UsuarioService:
    def __init__(self, db: Session):
        self.repo = UsuarioRepository(db)

    def criar_usuario(self, usuario_data: UsuarioCreate) -> Usuario:
        """Cria um novo usuário com senha hasheada."""
        # Verificar se email já existe
        if self.repo.get_by_email(usuario_data.email):
            raise ValueError("E-mail já cadastrado")

        # Hashear a senha
        usuario_dict = usuario_data.model_dump()
        senha = usuario_dict.pop("senha")
        usuario_dict["senha_hash"] = get_password_hash(senha)

        return self.repo.create(UsuarioCreate(**usuario_dict))

    def autenticar(self, email: str, senha: str) -> Usuario | None:
        """Autentica um usuário pelo email e senha."""
        usuario = self.repo.get_by_email(email)
        if not usuario:
            return None
        if not verify_password(senha, usuario.senha_hash):
            return None
        return usuario

    def obter_usuario(self, usuario_id: int) -> Usuario | None:
        return self.repo.get(usuario_id)

    def listar_usuarios(self, skip: int = 0, limit: int = 100):
        return self.repo.get_multi(skip, limit)

    def atualizar_usuario(self, usuario_id: int, usuario_data: UsuarioUpdate) -> Usuario | None:
        usuario = self.repo.get(usuario_id)
        if not usuario:
            return None

        update_data = usuario_data.model_dump(exclude_unset=True)
        if "senha" in update_data:
            senha = update_data.pop("senha")
            update_data["senha_hash"] = get_password_hash(senha)

        return self.repo.update(usuario, update_data)

    def deletar_usuario(self, usuario_id: int) -> bool:
        usuario = self.repo.get(usuario_id)
        if not usuario:
            return False
        self.repo.delete(usuario_id)
        return True