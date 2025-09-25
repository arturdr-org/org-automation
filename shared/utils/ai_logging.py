"""
Utilitário de logging por IA

Objetivo:
- Criar e usar pastas de log isoladas por agente/IA em logs/<ia_name>/
- Fornecer um logger pronto (logging.Logger) com FileHandler apontando para execution.log

Uso rápido:

    from shared.utils.ai_logging import get_logger, get_log_path

    logger = get_logger(ia_name="github_mcp")  # ou deixe None para ler IA_NAME do ambiente
    logger.info("Iniciando execução...")

    path = get_log_path("github_mcp")  # retorna pathlib.Path('logs/github_mcp')

Observações:
- Se ia_name não for informado, o util tentará ler IA_NAME (ou AI_NAME) do ambiente.
- Certifique-se de manter o diretório 'logs/' ignorado no VCS (já contemplado no .gitignore).
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

DEFAULT_BASE_DIR = Path("logs")
DEFAULT_LOG_FILENAME = "execution.log"


def _resolve_ia_name(ia_name: Optional[str]) -> str:
    if ia_name and ia_name.strip():
        return ia_name.strip()
    # Fallback para variáveis de ambiente
    env_name = os.getenv("IA_NAME") or os.getenv("AI_NAME")
    if env_name and env_name.strip():
        return env_name.strip()
    # Último fallback
    return "default_ai"


def get_log_path(ia_name: Optional[str] = None, base_dir: Path = DEFAULT_BASE_DIR) -> Path:
    """Retorna o caminho da pasta de logs para a IA, garantindo existência.

    Args:
        ia_name: Nome do agente/IA. Se None, usa IA_NAME/AI_NAME do ambiente.
        base_dir: Diretório base para logs (default: logs/).
    """
    name = _resolve_ia_name(ia_name)
    ia_dir = base_dir / name
    ia_dir.mkdir(parents=True, exist_ok=True)
    return ia_dir


def get_logger(
    ia_name: Optional[str] = None,
    *,
    level: int = logging.INFO,
    base_dir: Path = DEFAULT_BASE_DIR,
    log_filename: str = DEFAULT_LOG_FILENAME,
    logger_name_prefix: str = "ai",
) -> logging.Logger:
    """Cria/retorna um logger com FileHandler para logs/<ia_name>/execution.log.

    - propagate=False para evitar logs duplicados no root logger.
    - Não adiciona StreamHandler por padrão; foque em arquivos por IA.
    """
    name = _resolve_ia_name(ia_name)
    logger_name = f"{logger_name_prefix}.{name}"
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.propagate = False

    # Evitar múltiplos handlers se a função for chamada mais de uma vez
    if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        ia_dir = get_log_path(name, base_dir=base_dir)
        log_file = ia_dir / log_filename

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
