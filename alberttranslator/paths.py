"""Resolucion de rutas segun el modo de ejecucion (script vs. .exe congelado por PyInstaller).

`sys.frozen` es la bandera estandar que PyInstaller activa en el binario compilado.
Estas funciones evitan repetir esa comprobacion en cada modulo que necesita leer
plantillas, estaticos, el archivo `.env` o escribir logs.
"""

from __future__ import annotations

from pathlib import Path
import sys


def get_runtime_dir() -> Path:
    """Directorio donde viven los recursos empaquetados (templates/, static/).

    En el .exe, PyInstaller los descomprime en una carpeta temporal (`sys._MEIPASS`).
    En modo script, es la raiz del repositorio (dos niveles arriba de este archivo).
    """
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return Path(__file__).resolve().parent.parent


def get_external_dir() -> Path:
    """Directorio "junto al .exe" (o a la raiz del repo) para archivos que el
    usuario puede ver/editar en tiempo de ejecucion: `.env`, logs, cache de modelos.
    A diferencia de `get_runtime_dir()`, nunca apunta a la carpeta temporal de PyInstaller.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def get_env_path() -> Path:
    """Ruta del archivo `.env` de configuracion persistente del usuario."""
    return get_external_dir() / ".env"
