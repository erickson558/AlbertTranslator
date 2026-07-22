"""Punto de entrada fisico de AlbertTranslator.

Este es el archivo que PyInstaller compila (`build_exe.ps1` apunta a `app.py`).
Toda la logica real vive en el paquete `alberttranslator/`; aqui solo se
re-exportan los simbolos utiles para pruebas/otros scripts y se dispara
`run_entrypoint()` cuando se ejecuta directamente (`python app.py`).
"""

from __future__ import annotations

from alberttranslator.api import create_app
from alberttranslator.main import main, run_entrypoint

__all__ = ["create_app", "main", "run_entrypoint"]


if __name__ == "__main__":
    run_entrypoint()
