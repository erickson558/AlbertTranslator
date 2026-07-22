"""Configuracion centralizada de logging, hooks de excepciones no controladas y log de fallos fatales.

Todo el proyecto usa el logger nombrado "alberttranslator" (variable `LOGGER`) para
que un solo `RotatingFileHandler` capture GUI, servidor HTTP y motor de voz/traduccion
en un unico archivo (`alberttranslator.log`, junto al .exe).
"""

from __future__ import annotations

from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import sys
import threading
import traceback
import webbrowser
from typing import Dict

from .constants import FATAL_LOG_FILE, MAIN_LOG_FILE
from .paths import get_external_dir


LOGGER = logging.getLogger("alberttranslator")
# Evita volver a registrar handlers si configure_logging() se llama mas de una vez
# (por ejemplo, si main() y run_entrypoint() intentan inicializar logging cada uno).
_LOGGING_READY = False


def get_main_log_path() -> Path:
    """Ruta del log principal, siempre junto al .exe (o a la raiz en modo script)."""
    return get_external_dir() / MAIN_LOG_FILE


def configure_logging() -> Path:
    """Inicializa el root logger con salida a archivo rotativo (y consola en modo script).

    Idempotente: llamadas repetidas no duplican handlers gracias a `_LOGGING_READY`.
    """
    global _LOGGING_READY
    log_path = get_main_log_path()

    if _LOGGING_READY:
        return log_path

    log_path.parent.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(threadName)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Rota cada 2 MB y conserva 5 backups para no crecer sin limite en uso prolongado.
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=2 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    if not getattr(sys, "frozen", False):
        # En el .exe empaquetado (--windowed) no hay consola visible; solo se
        # agrega el handler de stdout cuando se ejecuta como script normal.
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # Silencia ruido de librerias de terceros que no aporta valor en el log principal.
    logging.getLogger("werkzeug").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("huggingface_hub").setLevel(logging.WARNING)
    logging.getLogger("argostranslate.utils").setLevel(logging.WARNING)
    _LOGGING_READY = True
    LOGGER.info("Logging inicializado. Archivo: %s", log_path)
    return log_path


def install_exception_hooks() -> None:
    """Registra hooks globales para que cualquier excepcion no controlada quede en el log
    en vez de perderse silenciosamente (proceso principal e hilos secundarios)."""

    def _sys_excepthook(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        LOGGER.exception(
            "Excepcion no controlada",
            exc_info=(exc_type, exc_value, exc_traceback),
        )

    def _thread_excepthook(args):
        LOGGER.exception(
            "Excepcion no controlada en hilo %s",
            args.thread.name if args.thread else "<desconocido>",
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
        )

    sys.excepthook = _sys_excepthook
    threading.excepthook = _thread_excepthook


def open_path(path: Path) -> None:
    """Abre un archivo con la aplicacion asociada del sistema operativo (usado por "Abrir logs")."""
    normalized = path.resolve()
    if os.name == "nt":
        os.startfile(str(normalized))  # type: ignore[attr-defined]
        return
    webbrowser.open(normalized.as_uri())


def safe_settings_for_log(settings: Dict[str, str]) -> Dict[str, str]:
    """Devuelve una copia de settings apta para loggear, ocultando claves/tokens/contrasenas."""
    redacted = {}
    for key in sorted(settings.keys()):
        value = settings[key]
        normalized_key = key.upper()
        if any(token in normalized_key for token in ("KEY", "TOKEN", "SECRET", "PASSWORD")):
            redacted[key] = "***"
        else:
            redacted[key] = value
    return redacted


def write_fatal_error(exc: Exception) -> Path:
    """Escribe un registro de error fatal (con traceback) en un archivo aparte del log rotativo,
    para que sobreviva incluso si el logging principal fallo al inicializarse."""
    log_path = get_external_dir() / FATAL_LOG_FILE
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = (
        f"[{timestamp}] Error fatal: {exc}\n"
        f"{traceback.format_exc()}\n"
        + ("-" * 80)
        + "\n"
    )
    try:
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(content)
    except Exception:
        pass
    return log_path
