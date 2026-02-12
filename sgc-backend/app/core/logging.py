import logging
from logging import Logger
import sys

from app.core.config import settings

def setup_logging() -> None:
    """
    Configura o logging da aplicação.
    - Em desenvolvimento: logs detalhados no console.
    - Em produção: pode ser adaptado para JSON, arquivo, etc.
    """
    log_level = logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO

    # Formato dos logs
    log_format = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler do console (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(log_format)

    # Configura o logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # Evita duplicação de handlers se a função for chamada mais de uma vez
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)
    else:
        root_logger.handlers.clear()
        root_logger.addHandler(console_handler)

    # Ajusta níveis de bibliotecas muito verbosas
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)  # Mude para DEBUG para ver SQL

def get_logger(name: str) -> Logger:
    """Retorna um logger com o nome do módulo."""
    return logging.getLogger(name)