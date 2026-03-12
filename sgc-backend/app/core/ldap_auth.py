"""
Autenticação via Active Directory (LDAP).

Fluxo:
  1. Tenta bind simples com as credenciais do usuário (UPN: email@dominio.com).
  2. Se bind OK → busca atributos do AD (nome, email) e retorna dict.
  3. Se senha errada (LDAPBindError) → retorna (False, None).
  4. Se servidor inacessível / erro de rede → retorna (None, None),
     sinalizando ao chamador que deve tentar o fallback local.
"""

import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def ldap_authenticate(email: str, password: str) -> Tuple[Optional[bool], Optional[dict]]:
    """
    Tenta autenticar no Active Directory.

    Retornos:
      (True,  info_dict) — credenciais válidas no AD; info_dict contém 'email' e 'nome'
      (False, None)      — senha incorreta (LDAPBindError)
      (None,  None)      — LDAP desabilitado, servidor inacessível ou erro inesperado
                           → o chamador pode tentar autenticação local como fallback
    """
    # Importação tardia para evitar ImportError se ldap3 não estiver instalado
    try:
        from ldap3 import Server, Connection, ALL, SIMPLE
        from ldap3.core.exceptions import LDAPBindError, LDAPException
    except ImportError:
        logger.error("Biblioteca 'ldap3' não instalada. Execute: pip install ldap3")
        return None, None

    from app.core.config import settings

    if not settings.LDAP_ENABLED or not settings.LDAP_SERVER:
        return None, None

    try:
        server = Server(
            settings.LDAP_SERVER,
            use_ssl=settings.LDAP_USE_SSL,
            get_info=ALL,
            connect_timeout=5,
        )

        conn = Connection(
            server,
            user=email,       # UPN: usuario@empresa.com.br
            password=password,
            authentication=SIMPLE,
            raise_exceptions=True,
        )
        conn.bind()

        # Credenciais válidas — buscar atributos do usuário
        user_info: dict = {"email": email, "nome": email.split("@")[0]}

        if settings.LDAP_BASE_DN:
            # Sanitizar email para uso em filtro LDAP
            safe_email = (
                email
                .replace("\\", "\\5c")
                .replace("*",  "\\2a")
                .replace("(",  "\\28")
                .replace(")",  "\\29")
                .replace("\0", "\\00")
            )
            conn.search(
                search_base=settings.LDAP_BASE_DN,
                search_filter=f"(userPrincipalName={safe_email})",
                attributes=["displayName", "cn", "mail"],
            )
            if conn.entries:
                entry = conn.entries[0]
                nome = (
                    str(entry.displayName) if entry.displayName
                    else (str(entry.cn) if entry.cn else None)
                )
                if nome:
                    user_info["nome"] = nome
                if entry.mail:
                    user_info["email"] = str(entry.mail)

        conn.unbind()
        return True, user_info

    except LDAPBindError:
        # Credenciais inválidas
        return False, None

    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "Erro ao conectar ao servidor LDAP '%s': %s. "
            "Tentando autenticação local como fallback.",
            settings.LDAP_SERVER,
            exc,
        )
        return None, None
