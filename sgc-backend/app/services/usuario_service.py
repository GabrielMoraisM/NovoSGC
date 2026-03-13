# app/services/usuario_service.py

import secrets
from typing import Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.usuario_repo import UsuarioRepository
from app.schemas.usuario import UsuarioCreate
from app.core.security import get_password_hash, verify_password
from app.core.config import settings


class UsuarioService:
    def __init__(self, db: Session):
        self.repo = UsuarioRepository(db)

    def create_usuario(self, usuario_in: UsuarioCreate):
        # Verificar se email já existe
        if self.repo.get_by_email(usuario_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
        # Preparar dados para criação (substituir senha por hash)
        usuario_data = usuario_in.dict()
        usuario_data['senha_hash'] = get_password_hash(usuario_data.pop('senha'))
        return self.repo.create(**usuario_data)

    def get_usuario_by_email(self, email: str):
        return self.repo.get_by_email(email)

    def get_usuario(self, usuario_id: int):
        return self.repo.get(usuario_id)

    # ----------------------------------------------------------------
    # Autenticação híbrida: Active Directory → fallback local
    # ----------------------------------------------------------------
    def authenticate(self, email: str, password: str):
        """
        1. Se LDAP_ENABLED: tenta autenticar no AD.
           - Sucesso AD   → provisiona o usuário no DB se necessário e retorna.
           - Senha errada → nega imediatamente (não testa senha local).
           - Servidor fora→ cai no fallback local (se LDAP_FALLBACK_LOCAL=True).
        2. Fallback local: verifica senha bcrypt armazenada no banco.
        """
        if settings.LDAP_ENABLED:
            from app.core.ldap_auth import ldap_authenticate
            ldap_ok, ldap_info = ldap_authenticate(email, password)

            if ldap_ok is True:
                # Credenciais válidas no AD
                # 1) Tenta achar pelo email de login (ex: @heca.corp)
                usuario = self.repo.get_by_email(email)
                # 2) O AD pode retornar um email diferente (ex: mail=@heca.com.br)
                #    Se não achou pelo login, tenta pelo email do AD
                if not usuario and ldap_info.get("email") and ldap_info["email"] != email:
                    usuario = self.repo.get_by_email(ldap_info["email"])
                if not usuario:
                    # Primeiro acesso: cria com o email de login para evitar duplicatas
                    provision_info = {**ldap_info, "email": email}
                    usuario = self._provision_ldap_user(provision_info)
                return usuario

            if ldap_ok is False:
                # Senha incorreta confirmada pelo AD → negar, sem fallback
                return None

            # ldap_ok is None → servidor inacessível
            if not settings.LDAP_FALLBACK_LOCAL:
                return None
            # Continua para verificação local abaixo

        # Autenticação local (senha bcrypt)
        usuario = self.repo.get_by_email(email)
        if not usuario:
            return None
        if not verify_password(password, usuario.senha_hash):
            return None
        return usuario

    def _provision_ldap_user(self, ldap_info: dict):
        """
        Cria um usuário no banco a partir das informações obtidas do AD.
        A senha é definida como um hash aleatório inutilizável — o usuário
        só consegue logar via AD.
        """
        # Hash impossível de adivinhar: ninguém sabe essa "senha"
        senha_placeholder = get_password_hash(f"LDAP_{secrets.token_hex(32)}")

        usuario = self.repo.create(
            nome=ldap_info.get("nome", ldap_info["email"].split("@")[0]),
            email=ldap_info["email"],
            senha_hash=senha_placeholder,
            perfil=settings.LDAP_DEFAULT_PERFIL,
            ativo=True,
        )
        # flush() não persiste — commit explícito necessário para salvar o novo usuário AD
        self.repo.db.commit()
        self.repo.db.refresh(usuario)
        return usuario
