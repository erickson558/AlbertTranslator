"""Shims e importes perezosos para dependencias pesadas u opcionales.

Estos modulos (`faster_whisper`, `argostranslate`) son caros de importar (tardan
o arrastran dependencias nativas como torch/onnxruntime) y no siempre estan
instalados segun el backend elegido por el usuario. Se importan solo cuando
realmente se necesitan (`ensure_*_import`), y se sustituyen dependencias
transitivas problematicas en el build portable de Windows por stubs livianos.
"""

from __future__ import annotations

import os
import re
import sys
import types

from .constants import DEFAULT_ARGOS_CHUNK_TYPE
from .logging_setup import LOGGER


# Cache de modulos ya importados; evitan reimportar/reinicializar en cada llamada.
WhisperModel = None
argos_package = None
argos_translate = None


def prepare_runtime_import_shims() -> None:
    """Instala stubs en `sys.modules` para dependencias transitivas de Argos que
    no se necesitan con la configuracion actual (ARGOS_CHUNK_TYPE=MINISBD) y que,
    en el build portable de Windows, pueden fallar al cargar (stanza/torch pesados,
    o la DLL nativa de onnxruntime que usa minisbd)."""
    # Argos importa stanza aunque usemos MiniSBD.
    # Creamos un stub liviano para evitar inicializar stanza/torch.
    if "stanza" not in sys.modules:
        stanza_stub = types.ModuleType("stanza")

        class _UnavailablePipeline:
            def __init__(self, *args, **kwargs):
                raise RuntimeError(
                    "Stanza esta deshabilitado en este build portable. "
                    "Usa ARGOS_CHUNK_TYPE=MINISBD."
                )

        stanza_stub.Pipeline = _UnavailablePipeline
        sys.modules["stanza"] = stanza_stub

    # En builds portables de Windows, minisbd puede fallar al cargar onnxruntime DLL.
    # Este shim mantiene una segmentacion simple para que Argos pueda traducir sin crashear.
    if "minisbd" not in sys.modules:
        minisbd_stub = types.ModuleType("minisbd")

        class _MiniSBDModels:
            cache_dir = ""

            @staticmethod
            def list_models():
                return [
                    "ar",
                    "de",
                    "en",
                    "es",
                    "fr",
                    "hi",
                    "it",
                    "ja",
                    "ko",
                    "nl",
                    "pl",
                    "pt",
                    "ru",
                    "sv",
                    "tr",
                    "uk",
                    "zh",
                ]

        class _MiniSBDetect:
            def __init__(self, *args, **kwargs):
                pass

            def sentences(self, text: str):
                # Segmentacion simple por puntuacion de cierre de oracion;
                # suficiente para el uso que Argos hace de este resultado.
                raw = str(text or "").strip()
                if not raw:
                    return []
                parts = [item.strip() for item in re.split(r"(?<=[.!?])\s+", raw) if item.strip()]
                return parts if parts else [raw]

        minisbd_stub.SBDetect = _MiniSBDetect
        minisbd_stub.models = _MiniSBDModels()
        sys.modules["minisbd"] = minisbd_stub


def ensure_whisper_import() -> None:
    """Importa `faster_whisper` de forma perezosa (solo si el backend `faster_whisper` esta activo)."""
    global WhisperModel
    if WhisperModel is not None:
        return

    prepare_runtime_import_shims()
    try:
        LOGGER.info("Importando faster-whisper...")
        from faster_whisper import WhisperModel as _WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "Dependencia faltante: instala faster-whisper para transcripcion sin conexion."
        ) from exc

    LOGGER.info("faster-whisper importado correctamente.")
    WhisperModel = _WhisperModel


def ensure_argos_imports() -> None:
    """Importa `argostranslate` de forma perezosa (traduccion 100% offline, no expuesta actualmente en la API)."""
    global argos_package, argos_translate
    if argos_package is not None and argos_translate is not None:
        return

    prepare_runtime_import_shims()
    os.environ.setdefault("ARGOS_CHUNK_TYPE", DEFAULT_ARGOS_CHUNK_TYPE)

    try:
        LOGGER.info("Importando Argos Translate...")
        import argostranslate.package as _argos_package
        import argostranslate.translate as _argos_translate
    except ImportError as exc:
        raise RuntimeError(
            "Dependencia faltante: instala argostranslate para traduccion sin conexion."
        ) from exc

    LOGGER.info("Argos Translate importado correctamente.")
    argos_package = _argos_package
    argos_translate = _argos_translate
