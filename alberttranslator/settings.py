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
    value = str(raw or "").strip().lower()
    if value not in {"cpu", "cuda", "auto"}:
        return DEFAULT_WHISPER_DEVICE

    # En builds portables de Windows, "auto" suele causar cierres por drivers/DLL.
    # Forzamos CPU para priorizar estabilidad.
    if os.name == "nt" and value == "auto":
        return "cpu"

    return value


def normalize_whisper_model(raw: str) -> str:
    value = str(raw or "").strip().lower()
    allowed = {"tiny", "base", "small", "medium", "large-v3"}
    return value if value in allowed else DEFAULT_WHISPER_MODEL


def normalize_translation_backend(raw: str) -> str:
    value = str(raw or "").strip().lower()
    allowed = {"google", "libretranslate"}
    return value if value in allowed else DEFAULT_TRANSLATION_BACKEND


def normalize_transcription_backend(raw: str) -> str:
    value = str(raw or "").strip().lower()
    allowed = {"faster_whisper", "google"}
    return value if value in allowed else DEFAULT_TRANSCRIPTION_BACKEND


def to_bool(value: str | bool | None) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def strict_port(raw: str) -> int:
    port = int(str(raw).strip())
    if port < 1 or port > 65535:
        raise ValueError("Puerto invalido")
    return port


def coerce_port(raw: str) -> int:
    try:
        return strict_port(raw)
    except Exception:
        return int(DEFAULT_PORT)


def strict_chunk_ms(raw: str) -> int:
    value = int(str(raw).strip())
    if value < 500 or value > 30000:
        raise ValueError("Bloque de audio invalido")
    return value


def coerce_chunk_ms(raw: str) -> int:
    try:
        return strict_chunk_ms(raw)
    except Exception:
        return int(DEFAULT_AUDIO_CHUNK_MS)


def strict_timeout_seconds(raw: str) -> float:
    value = float(str(raw).strip())
    if value <= 0:
        raise ValueError("Timeout invalido")
    return value


def coerce_timeout_seconds(raw: str) -> float:
    try:
        return strict_timeout_seconds(raw)
    except Exception:
        return float(DEFAULT_LIBRETRANSLATE_TIMEOUT_SEC)


def is_valid_language_code(value: str) -> bool:
    code = str(value).strip().lower()
    return len(code) >= 2 and len(code) <= 8 and code.isalpha()


def coerce_settings(raw: Dict[str, str] | None = None) -> Dict[str, str]:
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
    normalized = coerce_settings(settings)
    env_path = get_env_path()

    lines = []
    for key in DEFAULT_SETTINGS:
        value = normalized[key].replace("\n", "").replace("\r", "")
        lines.append(f"{key}={value}")

    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def apply_settings_to_env(settings: Dict[str, str]) -> None:
    normalized = coerce_settings(settings)
    for key, value in normalized.items():
        os.environ[key] = value
