"""Carga, validacion y persistencia de la configuracion del usuario (`.env`).

Toda la configuracion pasa por `coerce_settings()` antes de usarse, de modo que
GUI, CLI y API siempre trabajan con valores ya validados y con los mismos
defaults (`constants.DEFAULT_SETTINGS`) sin importar el origen del dato
(env vars del proceso, archivo `.env` o dict pasado explicitamente).
"""

from __future__ import annotations

import os
from typing import Dict

from dotenv import dotenv_values

from .constants import (
    DEFAULT_ARGOS_CHUNK_TYPE,
    DEFAULT_AUDIO_CHUNK_MS,
    DEFAULT_HOST,
    DEFAULT_LIBRETRANSLATE_TIMEOUT_SEC,
    DEFAULT_LIBRETRANSLATE_URL,
    DEFAULT_PORT,
    DEFAULT_SETTINGS,
    DEFAULT_TRANSCRIPTION_BACKEND,
    DEFAULT_TRANSLATION_BACKEND,
    DEFAULT_WHISPER_LOCAL_FILES_ONLY,
    DEFAULT_WHISPER_COMPUTE_TYPE,
    DEFAULT_WHISPER_DEVICE,
    DEFAULT_WHISPER_MODEL,
)
from .paths import get_env_path


def normalize_whisper_device(raw: str) -> str:
    """Normaliza el dispositivo de Whisper, forzando `cpu` cuando corresponde por estabilidad."""
    value = str(raw or "").strip().lower()
    if value not in {"cpu", "cuda", "auto"}:
        return DEFAULT_WHISPER_DEVICE

    # En builds portables de Windows, "auto" suele causar cierres por drivers/DLL.
    # Forzamos CPU para priorizar estabilidad.
    if os.name == "nt" and value == "auto":
        return "cpu"

    return value


def normalize_whisper_model(raw: str) -> str:
    """Restringe el modelo Whisper a la lista soportada por la GUI; si no es valido, usa el default."""
    value = str(raw or "").strip().lower()
    allowed = {"tiny", "base", "small", "medium", "large-v3"}
    return value if value in allowed else DEFAULT_WHISPER_MODEL


def normalize_translation_backend(raw: str) -> str:
    """Restringe el backend de traduccion a los valores soportados (`google`/`libretranslate`)."""
    value = str(raw or "").strip().lower()
    allowed = {"google", "libretranslate"}
    return value if value in allowed else DEFAULT_TRANSLATION_BACKEND


def normalize_transcription_backend(raw: str) -> str:
    """Restringe el backend de transcripcion a los valores soportados (`faster_whisper`/`google`)."""
    value = str(raw or "").strip().lower()
    allowed = {"faster_whisper", "google"}
    return value if value in allowed else DEFAULT_TRANSCRIPTION_BACKEND


def to_bool(value: str | bool | None) -> bool:
    """Convierte valores tipo booleano provenientes de `.env` (texto) o de la GUI (bool) a `bool`."""
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def strict_port(raw: str) -> int:
    """Valida un puerto TCP; lanza ValueError si esta fuera de rango (usado por la GUI para bloquear guardado)."""
    port = int(str(raw).strip())
    if port < 1 or port > 65535:
        raise ValueError("Puerto invalido")
    return port


def coerce_port(raw: str) -> int:
    """Version tolerante de `strict_port`: ante un valor invalido, cae al puerto por defecto."""
    try:
        return strict_port(raw)
    except Exception:
        return int(DEFAULT_PORT)


def strict_chunk_ms(raw: str) -> int:
    """Valida el tamano de bloque de audio (ms); lanza ValueError si esta fuera de rango."""
    value = int(str(raw).strip())
    if value < 500 or value > 30000:
        raise ValueError("Bloque de audio invalido")
    return value


def coerce_chunk_ms(raw: str) -> int:
    """Version tolerante de `strict_chunk_ms`: ante un valor invalido, cae al default."""
    try:
        return strict_chunk_ms(raw)
    except Exception:
        return int(DEFAULT_AUDIO_CHUNK_MS)


def strict_timeout_seconds(raw: str) -> float:
    """Valida un timeout en segundos (> 0); lanza ValueError si es invalido."""
    value = float(str(raw).strip())
    if value <= 0:
        raise ValueError("Timeout invalido")
    return value


def coerce_timeout_seconds(raw: str) -> float:
    """Version tolerante de `strict_timeout_seconds`: ante un valor invalido, cae al default."""
    try:
        return strict_timeout_seconds(raw)
    except Exception:
        return float(DEFAULT_LIBRETRANSLATE_TIMEOUT_SEC)


def is_valid_language_code(value: str) -> bool:
    """Valida codigos de idioma tipo ISO-639 usados en toda la app (frontend, API y motor de voz).

    Acepta codigos simples ("en", "es") y con subtag regional separado por
    guion ("zh-cn", "zh-tw"). Antes se usaba `str.isalpha()`, que rechazaba
    cualquier codigo con guion; por eso existe esta funcion dedicada.
    """
    code = str(value).strip().lower()
    if not code or len(code) > 16:
        return False
    parts = code.split("-")
    return (
        len(parts) <= 2
        and all(2 <= len(p) <= 8 and p.isalpha() for p in parts)
    )


def coerce_settings(raw: Dict[str, str] | None = None) -> Dict[str, str]:
    """Combina `raw` con los defaults y normaliza/valida cada campo.

    Es el unico punto donde se garantiza que un dict de settings es "seguro
    de usar": puertos y timeouts numericos validos, backends restringidos a
    valores soportados, booleanos normalizados a "0"/"1".
    """
    data = DEFAULT_SETTINGS.copy()
    if raw:
        for key in data:
            value = raw.get(key)
            if value is not None:
                data[key] = str(value).strip()

    if not data["APP_HOST"]:
        data["APP_HOST"] = DEFAULT_HOST
    if not data["WHISPER_MODEL"]:
        data["WHISPER_MODEL"] = DEFAULT_WHISPER_MODEL
    if not data["WHISPER_DEVICE"]:
        data["WHISPER_DEVICE"] = DEFAULT_WHISPER_DEVICE
    if not data["WHISPER_COMPUTE_TYPE"]:
        data["WHISPER_COMPUTE_TYPE"] = DEFAULT_WHISPER_COMPUTE_TYPE
    if not data["ARGOS_CHUNK_TYPE"]:
        data["ARGOS_CHUNK_TYPE"] = DEFAULT_ARGOS_CHUNK_TYPE
    if not data["TRANSCRIPTION_BACKEND"]:
        data["TRANSCRIPTION_BACKEND"] = DEFAULT_TRANSCRIPTION_BACKEND
    if not data["WHISPER_LOCAL_FILES_ONLY"]:
        data["WHISPER_LOCAL_FILES_ONLY"] = DEFAULT_WHISPER_LOCAL_FILES_ONLY
    if not data["TRANSLATION_BACKEND"]:
        data["TRANSLATION_BACKEND"] = DEFAULT_TRANSLATION_BACKEND
    if not data["LIBRETRANSLATE_URL"]:
        data["LIBRETRANSLATE_URL"] = DEFAULT_LIBRETRANSLATE_URL
    if not data["LIBRETRANSLATE_TIMEOUT_SEC"]:
        data["LIBRETRANSLATE_TIMEOUT_SEC"] = DEFAULT_LIBRETRANSLATE_TIMEOUT_SEC

    data["APP_PORT"] = str(coerce_port(data["APP_PORT"]))
    data["AUDIO_CHUNK_MS"] = str(coerce_chunk_ms(data["AUDIO_CHUNK_MS"]))
    data["WHISPER_MODEL"] = normalize_whisper_model(data["WHISPER_MODEL"])
    data["WHISPER_DEVICE"] = normalize_whisper_device(data["WHISPER_DEVICE"])
    data["TRANSCRIPTION_BACKEND"] = normalize_transcription_backend(
        data["TRANSCRIPTION_BACKEND"]
    )
    data["WHISPER_LOCAL_FILES_ONLY"] = (
        "1" if to_bool(data["WHISPER_LOCAL_FILES_ONLY"]) else "0"
    )
    data["TRANSLATION_BACKEND"] = normalize_translation_backend(data["TRANSLATION_BACKEND"])
    data["LIBRETRANSLATE_URL"] = (
        str(data["LIBRETRANSLATE_URL"]).strip().rstrip("/") or DEFAULT_LIBRETRANSLATE_URL
    )
    data["LIBRETRANSLATE_TIMEOUT_SEC"] = str(
        coerce_timeout_seconds(data["LIBRETRANSLATE_TIMEOUT_SEC"])
    )
    data["ARGOS_CHUNK_TYPE"] = data["ARGOS_CHUNK_TYPE"].strip().upper()
    data["LIBRETRANSLATE_API_KEY"] = str(data["LIBRETRANSLATE_API_KEY"]).strip()
    data["APP_OPEN_BROWSER"] = "1" if to_bool(data["APP_OPEN_BROWSER"]) else "0"
    data["AUTO_INSTALL_TRANSLATION_PACKAGES"] = (
        "1" if to_bool(data["AUTO_INSTALL_TRANSLATION_PACKAGES"]) else "0"
    )

    return data


def load_settings() -> Dict[str, str]:
    """Carga settings combinando, en orden de prioridad: defaults < `.env` < variables de entorno del proceso."""
    env_path = get_env_path()

    merged = DEFAULT_SETTINGS.copy()
    if env_path.exists():
        values = dotenv_values(env_path)
        for key in merged:
            if key in values and values[key] is not None:
                merged[key] = str(values[key]).strip()

    for key in merged:
        env_value = os.getenv(key)
        if env_value is not None and str(env_value).strip() != "":
            merged[key] = str(env_value).strip()

    return coerce_settings(merged)


def save_settings(settings: Dict[str, str]) -> None:
    """Escribe los settings normalizados en el archivo `.env` (usado por el boton "Guardar config")."""
    normalized = coerce_settings(settings)
    env_path = get_env_path()

    lines = []
    for key in DEFAULT_SETTINGS:
        value = normalized[key].replace("\n", "").replace("\r", "")
        lines.append(f"{key}={value}")

    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def apply_settings_to_env(settings: Dict[str, str]) -> None:
    """Vuelca los settings normalizados a `os.environ` del proceso actual (para que subprocesos/librerias los vean)."""
    normalized = coerce_settings(settings)
    for key, value in normalized.items():
        os.environ[key] = value
