from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Banco de Dados
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Ambiente (development, production)
    ENVIRONMENT: str = "development"

    # ----------------------------------------------------------------
    # Active Directory / LDAP
    # ----------------------------------------------------------------
    # Habilitar integração com AD (False = somente autenticação local)
    LDAP_ENABLED: bool = False

    # Endereço do servidor AD. Exemplos:
    #   "ldap://10.40.20.10"       → LDAP padrão (porta 389)
    #   "ldaps://ad.empresa.com"   → LDAP com SSL (porta 636)
    LDAP_SERVER: str = ""

    # Usar SSL/TLS (recomendado em produção)
    LDAP_USE_SSL: bool = False

    # Base DN para busca de usuários. Exemplo:
    #   "DC=heca,DC=com,DC=br"
    LDAP_BASE_DN: str = ""

    # Perfil padrão atribuído a novos usuários provisionados pelo AD
    # Opções: ADMIN, GESTOR, FINANCEIRO, AUDITOR, TI
    LDAP_DEFAULT_PERFIL: str = "GESTOR"

    # Se True: quando o servidor LDAP estiver inacessível, tenta a
    # senha local do SGC como fallback (mais resiliente, menos seguro).
    # Se False: nega o login se o LDAP estiver fora do ar.
    LDAP_FALLBACK_LOCAL: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",          # carrega do arquivo .env
        env_file_encoding="utf-8",
        case_sensitive=False
    )

# Instância única para ser importada em toda a aplicação
settings = Settings()