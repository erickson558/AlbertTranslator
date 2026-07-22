"""Motor de transcripcion (speech-to-text) y traduccion usado por la API Flask.

Contiene:
- `OfflineSpeechEngine`: fachada con estado (cachea el modelo Whisper cargado)
  que expone transcripcion y traduccion con el backend configurado.
- Funciones de transcripcion por backend (`transcribe_with_google`,
  `transcribe_with_faster_whisper`) y de traduccion por backend
  (`translate_with_google`, `translate_with_libretranslate`).
- Utilidades de normalizacion de codigos de idioma entre los distintos
  formatos que exige cada backend (ISO simple, regional tipo BCP-47, etc.).

El nombre "Offline" es historico: el proyecto empezo con backends 100% locales
(Whisper + Argos Translate) y hoy tambien soporta backends en la nube
(Google Speech/Translate, LibreTranslate) seleccionables por el usuario.
"""

from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
import tempfile
from typing import Dict
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from .logging_setup import LOGGER
from .paths import get_external_dir, get_runtime_dir
from .runtime_dependencies import ensure_whisper_import
import alberttranslator.runtime_dependencies as runtime_dependencies


_LANGDETECT_FACTORY_SEEDED = False
# Protege la inicializacion del seed de langdetect contra condiciones de carrera en Flask multi-hilo
_LANGDETECT_SEED_LOCK = Lock()
# Cachea instancias de GoogleTranslator por par (origen, destino) para no recrearlas en cada bloque.
_GOOGLE_TRANSLATOR_CACHE: dict[tuple[str, str], object] = {}
_GOOGLE_TRANSLATOR_CACHE_LOCK = Lock()


class TranslationPairError(RuntimeError):
    """Se lanza cuando no se puede traducir el texto."""


class OfflineSpeechEngine:
    """Fachada de transcripcion + traduccion; una instancia por app Flask (ver `create_app`).

    Mantiene en memoria el modelo Whisper ya cargado (costoso de inicializar)
    para reutilizarlo entre requests en vez de recargarlo en cada bloque de audio.
    """

    def __init__(self, settings: Dict[str, str]) -> None:
        self.settings = settings
        self._whisper_model = None
        self._whisper_model_source = ""
        # Evita que dos requests concurrentes disparen la carga del modelo dos veces.
        self._whisper_model_lock = Lock()
        self._whisper_error = ""

        transcription_backend = normalize_transcription_backend(
            settings.get("TRANSCRIPTION_BACKEND", "google")
        )
        backend = normalize_translation_backend(settings.get("TRANSLATION_BACKEND", "google"))
        LOGGER.info(
            "Motor offline inicializado. stt_backend=%s model=%s device=%s compute_type=%s local_files_only=%s auto_install_pairs=%s translation_backend=%s",
            transcription_backend,
            settings.get("WHISPER_MODEL", "base"),
            settings.get("WHISPER_DEVICE", "cpu"),
            settings.get("WHISPER_COMPUTE_TYPE", "int8"),
            settings.get("WHISPER_LOCAL_FILES_ONLY", "1"),
            settings.get("AUTO_INSTALL_TRANSLATION_PACKAGES", "1"),
            backend,
        )

    def transcribe_file(
        self,
        audio_path: Path,
        source_language: str,
        language_hint: str = "",
        transcription_backend_override: str | None = None,
    ) -> tuple[str, str]:
        """Transcribe un archivo de audio con el backend activo (o el override recibido en la request).

        Devuelve `(texto_transcrito, idioma_detectado)`. El idioma detectado se
        usa luego como idioma origen real cuando el usuario eligio "auto".
        """
        backend = normalize_transcription_backend(
            transcription_backend_override or self.transcription_backend()
        )
        LOGGER.info(
            "Transcribiendo audio. backend=%s source=%s hint=%s file=%s",
            backend,
            source_language,
            language_hint,
            audio_path,
        )

        if backend == "google":
            transcript_text = transcribe_with_google(
                audio_path=audio_path,
                source_language=source_language,
                language_hint=language_hint,
            )
            if source_language == "auto":
                detected_language = (
                    detect_language_code(transcript_text)
                    or normalize_language_hint(language_hint)
                    or "auto"
                )
            else:
                detected_language = source_language
        else:
            transcript_text, detected_language = transcribe_with_faster_whisper(
                audio_path=audio_path,
                source_language=source_language,
                language_hint=language_hint,
                model=self._ensure_whisper_model(),
            )

        LOGGER.info(
            "Transcripcion finalizada. backend=%s detected_language=%s chars=%s",
            backend,
            detected_language,
            len(transcript_text),
        )
        return transcript_text, detected_language

    def translate_text(
        self,
        transcript: str,
        source_language: str,
        detected_language: str,
        target_language: str,
    ) -> str:
        """Traduce un texto ya transcrito usando el backend de traduccion configurado.

        Si el idioma origen resuelto coincide con el destino, se devuelve el
        texto sin cambios (evita una llamada de red innecesaria).
        """
        backend = self.translation_backend()
        source_for_translation = detected_language if source_language == "auto" else source_language
        source_for_translation = (source_for_translation or "").strip().lower()
        target_language = (target_language or "").strip().lower()

        LOGGER.info(
            "Traduciendo texto. source=%s target=%s chars=%s backend=%s",
            source_for_translation,
            target_language,
            len(transcript),
            backend,
        )

        if not target_language:
            raise TranslationPairError("No se especifico idioma destino.")

        if not source_for_translation:
            source_for_translation = "auto"

        if source_for_translation == target_language:
            return transcript

        translated = translate_with_backend(
            transcript=transcript,
            source_language=source_for_translation,
            target_language=target_language,
            settings=self.settings,
        )

        LOGGER.info(
            "Traduccion completada. source=%s target=%s chars=%s backend=%s",
            source_for_translation,
            target_language,
            len(translated),
            backend,
        )
        return translated

    def translation_backend(self) -> str:
        """Backend de traduccion normalizado segun los settings actuales."""
        return normalize_translation_backend(self.settings.get("TRANSLATION_BACKEND", "google"))

    def transcription_backend(self) -> str:
        """Backend de transcripcion normalizado segun los settings actuales."""
        return normalize_transcription_backend(
            self.settings.get("TRANSCRIPTION_BACKEND", "google")
        )

    def model_status(self) -> Dict[str, str | bool]:
        """Estado del modelo de transcripcion para `/api/health` y `/api/model-status`.

        Con backend `google` siempre reporta "ready" (no hay modelo local que cargar).
        """
        if self.transcription_backend() == "google":
            return {
                "state": "ready",
                "ready": True,
                "has_local_model": False,
                "error": "",
            }

        local_model = find_local_whisper_model(
            model_name=self.settings.get("WHISPER_MODEL", "base")
        )
        ready = self._whisper_model is not None
        has_local_model = local_model is not None
        return {
            "state": "ready" if ready else "idle",
            "ready": ready,
            "has_local_model": has_local_model,
            "error": self._whisper_error,
        }

    def start_model_warmup(self) -> bool:
        """Dispara la carga del modelo Whisper por adelantado (llamado desde `/api/preload-model`)."""
        if self.transcription_backend() != "faster_whisper":
            return False
        self._ensure_whisper_model()
        return True

    def _ensure_whisper_model(self):
        """Carga (una sola vez) y cachea el modelo `faster-whisper` configurado.

        Usa double-checked locking: la comprobacion rapida sin lock evita el
        costo de adquirir el Lock en el camino comun (modelo ya cargado);
        la comprobacion dentro del lock evita que dos hilos carguen el modelo
        dos veces si llegan al mismo tiempo con el modelo aun no listo.
        """
        if self._whisper_model is not None:
            return self._whisper_model

        with self._whisper_model_lock:
            if self._whisper_model is not None:
                return self._whisper_model

            model_name = str(self.settings.get("WHISPER_MODEL", "base")).strip().lower()
            device = str(self.settings.get("WHISPER_DEVICE", "cpu")).strip().lower() or "cpu"
            compute_type = str(self.settings.get("WHISPER_COMPUTE_TYPE", "int8")).strip()
            local_only = to_bool_like(self.settings.get("WHISPER_LOCAL_FILES_ONLY", "1"))
            download_root = resolve_whisper_download_root()
            model_source = resolve_whisper_model_source(model_name)

            if local_only and not model_source.exists():
                self._whisper_error = (
                    "No se encontro el modelo Whisper local. "
                    f"Esperado: {model_source}"
                )
                raise RuntimeError(
                    self._whisper_error
                    + ". Ajusta WHISPER_MODEL o desactiva WHISPER_LOCAL_FILES_ONLY=0 para permitir descarga."
                )

            try:
                ensure_whisper_import()
                whisper_cls = runtime_dependencies.WhisperModel
                self._whisper_model = whisper_cls(
                    str(model_source) if model_source.exists() else model_name,
                    device=device,
                    compute_type=compute_type,
                    download_root=str(download_root),
                    local_files_only=local_only,
                )
                self._whisper_model_source = (
                    str(model_source) if model_source.exists() else model_name
                )
                self._whisper_error = ""
                LOGGER.info(
                    "Modelo Whisper listo. source=%s device=%s compute_type=%s local_only=%s",
                    self._whisper_model_source,
                    device,
                    compute_type,
                    local_only,
                )
            except Exception as exc:
                self._whisper_error = str(exc)
                raise RuntimeError(
                    f"No se pudo inicializar faster-whisper: {exc}"
                ) from exc

        return self._whisper_model


def transcribe_with_google(
    audio_path: Path,
    source_language: str,
    language_hint: str,
) -> str:
    """Transcribe un archivo de audio usando el backend `google` (via `SpeechRecognition`)."""
    try:
        import speech_recognition as sr
    except Exception as exc:
        raise RuntimeError(
            "Dependencia faltante: instala SpeechRecognition para transcripcion."
        ) from exc

    recognizer = sr.Recognizer()
    stt_language = normalize_stt_language(source_language, language_hint)

    try:
        with sr.AudioFile(str(audio_path)) as source:
            audio_data = recognizer.record(source)
    except Exception as exc:
        raise RuntimeError(f"No se pudo leer el audio recibido: {exc}") from exc

    try:
        text = recognizer.recognize_google(audio_data, language=stt_language)
    except sr.UnknownValueError:
        # No se detecto habla en el bloque; no es un error, se devuelve vacio.
        return ""
    except sr.RequestError as exc:
        raise RuntimeError(
            "No se pudo conectar al servicio de reconocimiento de voz. "
            f"Detalle: {exc}"
        ) from exc
    except Exception as exc:
        raise RuntimeError(f"Fallo en transcripcion de voz: {exc}") from exc

    return str(text or "").strip()


def transcribe_with_faster_whisper(
    audio_path: Path,
    source_language: str,
    language_hint: str,
    model,
) -> tuple[str, str]:
    """Transcribe un archivo de audio usando un modelo `faster-whisper` ya cargado."""
    transcription_language = normalize_whisper_language_code(source_language)
    if not transcription_language and source_language != "auto":
        transcription_language = normalize_whisper_language_code(language_hint)

    kwargs = {
        "task": "transcribe",
        "beam_size": 1,
        "vad_filter": True,
        "condition_on_previous_text": False,
    }
    if transcription_language:
        kwargs["language"] = transcription_language

    try:
        segments, info = model.transcribe(str(audio_path), **kwargs)
    except Exception as exc:
        raise RuntimeError(f"Fallo la transcripcion con faster-whisper: {exc}") from exc

    merged_segments = []
    for segment in segments:
        text = str(getattr(segment, "text", "") or "").strip()
        if text:
            merged_segments.append(text)

    transcript_text = " ".join(merged_segments).strip()
    if source_language == "auto":
        detected_language = normalize_whisper_language_code(
            str(getattr(info, "language", "") or "")
        ) or detect_language_code(transcript_text) or "auto"
    else:
        detected_language = normalize_whisper_language_code(source_language) or source_language

    return transcript_text, detected_language


def normalize_stt_language(source_language: str, language_hint: str) -> str:
    """Convierte un codigo simple ("es") al formato regional que exige la API de Google Speech ("es-ES")."""
    aliases = {
        "ar": "ar-SA",
        "de": "de-DE",
        "el": "el-GR",
        "en": "en-US",
        "es": "es-ES",
        "fr": "fr-FR",
        "he": "he-IL",
        "hi": "hi-IN",
        "it": "it-IT",
        "ja": "ja-JP",
        "ko": "ko-KR",
        "nl": "nl-NL",
        "pl": "pl-PL",
        "pt": "pt-PT",
        "ru": "ru-RU",
        "sv": "sv-SE",
        "tr": "tr-TR",
        "uk": "uk-UA",
        "zh": "zh-CN",
    }

    source = str(source_language or "").strip().lower()
    if source and source != "auto":
        return aliases.get(source, f"{source}-{source.upper()}")

    hint = normalize_language_hint(language_hint)
    if hint:
        return aliases.get(hint, f"{hint}-{hint.upper()}")

    return "es-ES"


def normalize_language_hint(language_hint: str) -> str:
    """Extrae y valida un codigo base de idioma (2-8 letras) desde el `language_hint` del navegador."""
    raw = str(language_hint or "").strip().lower()
    if not raw:
        return ""

    candidate = raw.split("-")[0].strip()
    if len(candidate) < 2 or len(candidate) > 8:
        return ""
    if not candidate.isalpha():
        return ""
    return candidate


def guess_extension(mime_type: str | None) -> str:
    """Deriva una extension de archivo a partir del mime type del blob de audio subido."""
    if not mime_type:
        return "wav"

    normalized = mime_type.lower()
    if "wav" in normalized:
        return "wav"
    if "ogg" in normalized:
        return "ogg"
    if "mpeg" in normalized or "mp3" in normalized:
        return "mp3"
    if "mp4" in normalized or "m4a" in normalized:
        return "m4a"
    if "webm" in normalized:
        return "webm"
    return "wav"


def write_temp_audio(audio_bytes: bytes, extension: str) -> Path:
    """Escribe el audio recibido a un archivo temporal (los motores de STT necesitan una ruta en disco)."""
    with tempfile.NamedTemporaryFile(suffix=f".{extension}", delete=False) as temp_file:
        temp_file.write(audio_bytes)
        return Path(temp_file.name)


def safe_delete_file(path: Path | None) -> None:
    """Borra un archivo temporal ignorando errores (no debe interrumpir la respuesta HTTP)."""
    if path is None:
        return
    try:
        path.unlink(missing_ok=True)
    except Exception:
        pass


def detect_language_code(text: str) -> str | None:
    """Detecta el idioma de un texto usando `langdetect`; devuelve `None` si no es concluyente."""
    sample = str(text or "").strip()
    if len(sample) < 3:
        return None

    try:
        from langdetect import DetectorFactory, LangDetectException, detect
    except Exception:
        return None

    # Double-checked locking: evita re-entrada innecesaria al lock en el caso mas comun
    global _LANGDETECT_FACTORY_SEEDED
    if not _LANGDETECT_FACTORY_SEEDED:
        with _LANGDETECT_SEED_LOCK:
            if not _LANGDETECT_FACTORY_SEEDED:
                # Semilla fija: hace determinista la deteccion (langdetect es probabilistico).
                DetectorFactory.seed = 0
                _LANGDETECT_FACTORY_SEEDED = True

    try:
        detected = str(detect(sample)).strip().lower()
    except LangDetectException:
        return None
    except Exception:
        return None

    if not detected:
        return None

    base_code = detected.split("-")[0].strip()
    if len(base_code) < 2 or len(base_code) > 8 or not base_code.isalpha():
        return None

    return base_code


def normalize_transcription_backend(raw: str) -> str:
    """Restringe el backend de transcripcion recibido a los valores soportados."""
    value = str(raw or "").strip().lower()
    return value if value in {"faster_whisper", "google"} else "google"


def _cached_google_translator(source_code: str, target_code: str):
    """Devuelve (creando si hace falta) el `GoogleTranslator` cacheado para este par de idiomas."""
    key = (source_code, target_code)
    with _GOOGLE_TRANSLATOR_CACHE_LOCK:
        translator = _GOOGLE_TRANSLATOR_CACHE.get(key)
        if translator is not None:
            return translator

        from deep_translator import GoogleTranslator

        translator = GoogleTranslator(source=source_code, target=target_code)
        _GOOGLE_TRANSLATOR_CACHE[key] = translator
        return translator


def to_bool_like(value: str | bool | None) -> bool:
    """Igual que `settings.to_bool`, duplicado aqui para no crear un ciclo de imports con `settings`."""
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def normalize_whisper_language_code(raw: str) -> str:
    """Convierte un codigo de idioma al formato simple (2-8 letras) que espera `faster-whisper`."""
    value = str(raw or "").strip().lower()
    if not value or value == "auto":
        return ""

    aliases = {
        "zh-cn": "zh",
        "zh-tw": "zh",
        "iw": "he",
    }
    normalized = aliases.get(value, value)

    if "-" in normalized:
        normalized = normalized.split("-")[0].strip()

    if len(normalized) < 2 or len(normalized) > 8 or not normalized.isalpha():
        return ""
    return normalized


def resolve_whisper_download_root() -> Path:
    """Directorio donde `faster-whisper` descarga/busca modelos (junto al .exe o al proyecto)."""
    candidates = [
        get_external_dir() / "models" / "whisper",
        get_runtime_dir() / "models" / "whisper",
    ]
    for path in candidates:
        try:
            path.mkdir(parents=True, exist_ok=True)
            return path
        except Exception:
            continue
    return get_external_dir()


def resolve_whisper_model_source(model_name: str) -> Path:
    """Resuelve la ruta local de un modelo Whisper si existe, o una ruta candidata para descargarlo."""
    local = find_local_whisper_model(model_name)
    if local is not None:
        return local

    raw = str(model_name or "").strip()
    if raw:
        candidate = Path(raw)
        if candidate.exists():
            return candidate

    return Path(raw or "base")


def find_local_whisper_model(model_name: str) -> Path | None:
    """Busca un modelo Whisper ya descargado en las ubicaciones de cache conocidas."""
    normalized = str(model_name or "").strip().lower() or "base"
    candidates = []
    seen = set()

    for root in (get_external_dir(), get_runtime_dir(), Path.cwd()):
        cache_root = root / "models" / "whisper"
        key = str(cache_root).lower()
        if key not in seen:
            seen.add(key)
            candidates.append(cache_root)

    for cache_root in candidates:
        if not cache_root.exists():
            continue

        direct = cache_root / normalized
        if (direct / "model.bin").exists():
            return direct

        repo_dir = cache_root / f"models--Systran--faster-whisper-{normalized}"
        snapshot = find_latest_snapshot_with_model(repo_dir)
        if snapshot is not None:
            return snapshot

    return None


def find_latest_snapshot_with_model(repo_dir: Path) -> Path | None:
    """Encuentra el snapshot mas reciente de un repo de HuggingFace Hub que contenga `model.bin`."""
    if not repo_dir.exists():
        return None
    if (repo_dir / "model.bin").exists():
        return repo_dir

    snapshots_dir = repo_dir / "snapshots"
    if not snapshots_dir.exists():
        return None

    snapshots = [path for path in snapshots_dir.iterdir() if path.is_dir()]
    snapshots.sort(key=lambda item: item.stat().st_mtime, reverse=True)

    for snapshot in snapshots:
        if (snapshot / "model.bin").exists():
            return snapshot
    return None


def translate_with_google(
    transcript: str,
    source_language: str,
    target_language: str,
) -> str:
    """Traduce texto usando Google Translate (via `deep-translator`, sin API key)."""
    try:
        from deep_translator import GoogleTranslator
    except Exception as exc:
        raise RuntimeError(
            "Dependencia faltante: instala deep-translator para traduccion."
        ) from exc

    source_code = normalize_google_language_code(source_language, allow_auto=True)
    target_code = normalize_google_language_code(target_language, allow_auto=False)

    try:
        # Reusar instancia evita crear objeto en cada bloque y reduce latencia percibida.
        translator = _cached_google_translator(source_code, target_code)
        translated = translator.translate(str(transcript or "").strip())
    except Exception as exc:
        raise RuntimeError(f"No se pudo traducir texto: {exc}") from exc

    return str(translated or "").strip()


def translate_with_libretranslate(
    transcript: str,
    source_language: str,
    target_language: str,
    settings: Dict[str, str],
) -> str:
    """Traduce texto llamando a una instancia de LibreTranslate (autoalojada o remota) por HTTP."""
    base_url = str(settings.get("LIBRETRANSLATE_URL", "http://127.0.0.1:5000")).strip().rstrip("/")
    if not base_url:
        base_url = "http://127.0.0.1:5000"

    timeout_seconds = parse_timeout_seconds(settings.get("LIBRETRANSLATE_TIMEOUT_SEC", "15"))
    source_code = normalize_libretranslate_language_code(source_language, allow_auto=True)
    target_code = normalize_libretranslate_language_code(target_language, allow_auto=False)

    payload = {
        "q": str(transcript or "").strip(),
        "source": source_code,
        "target": target_code,
        "format": "text",
    }

    api_key = str(settings.get("LIBRETRANSLATE_API_KEY", "")).strip()
    if api_key:
        payload["api_key"] = api_key

    data = urllib_parse.urlencode(payload).encode("utf-8")
    endpoint = f"{base_url}/translate"
    request = urllib_request.Request(
        endpoint,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
    )

    try:
        with urllib_request.urlopen(request, timeout=timeout_seconds) as response:
            raw_body = response.read().decode("utf-8", errors="replace")
    except urllib_error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        hint = extract_libretranslate_error(detail)
        raise RuntimeError(
            f"LibreTranslate devolvio HTTP {exc.code} en {endpoint}. {hint}"
        ) from exc
    except urllib_error.URLError as exc:
        raise RuntimeError(
            f"No se pudo conectar a LibreTranslate en {endpoint}. "
            "Verifica LIBRETRANSLATE_URL."
        ) from exc
    except TimeoutError as exc:
        raise RuntimeError(
            "Timeout al consultar LibreTranslate. "
            "Aumenta LIBRETRANSLATE_TIMEOUT_SEC o revisa el servidor."
        ) from exc
    except Exception as exc:
        raise RuntimeError(f"Error inesperado al llamar LibreTranslate: {exc}") from exc

    try:
        payload_json = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise RuntimeError("LibreTranslate respondio con JSON invalido.") from exc

    translated = str(payload_json.get("translatedText", "")).strip()
    if not translated:
        detail = extract_libretranslate_error(raw_body)
        raise RuntimeError(f"LibreTranslate no devolvio traduccion. {detail}")

    return translated


def translate_with_backend(
    transcript: str,
    source_language: str,
    target_language: str,
    settings: Dict[str, str],
) -> str:
    """Despacha la traduccion al backend configurado (`google` o `libretranslate`)."""
    backend = normalize_translation_backend(settings.get("TRANSLATION_BACKEND", "google"))
    if backend == "libretranslate":
        return translate_with_libretranslate(
            transcript=transcript,
            source_language=source_language,
            target_language=target_language,
            settings=settings,
        )
    return translate_with_google(
        transcript=transcript,
        source_language=source_language,
        target_language=target_language,
    )


def normalize_translation_backend(raw: str) -> str:
    """Restringe el backend de traduccion recibido a los valores soportados."""
    value = str(raw or "").strip().lower()
    return value if value in {"google", "libretranslate"} else "google"


def parse_timeout_seconds(raw: str) -> float:
    """Parsea un timeout en segundos desde texto; ante valor invalido/negativo cae a 15s."""
    try:
        value = float(str(raw).strip())
    except Exception:
        return 15.0
    return value if value > 0 else 15.0


def extract_libretranslate_error(raw: str) -> str:
    """Extrae un mensaje de error legible de una respuesta HTTP de LibreTranslate (JSON o texto plano)."""
    body = str(raw or "").strip()
    if not body:
        return "Sin detalle de error."

    try:
        parsed = json.loads(body)
    except Exception:
        return body[:240]

    for key in ("error", "message"):
        value = parsed.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return body[:240]


def normalize_google_language_code(code: str, allow_auto: bool) -> str:
    """Adapta un codigo de idioma al dialecto exacto que espera Google Translate (p. ej. `zh` -> `zh-cn`)."""
    value = str(code or "").strip().lower()
    if allow_auto and (not value or value == "auto"):
        return "auto"

    if not value:
        return "en"

    aliases = {
        "zh": "zh-cn",
        "zh-cn": "zh-cn",
        "zh-tw": "zh-tw",
        "he": "iw",
    }
    return aliases.get(value, value)


def normalize_libretranslate_language_code(code: str, allow_auto: bool) -> str:
    """Adapta un codigo de idioma al formato que espera la API de LibreTranslate."""
    value = str(code or "").strip().lower()
    if allow_auto and (not value or value == "auto"):
        return "auto"

    if not value:
        return "en"

    aliases = {
        "zh-cn": "zh",
        "zh-tw": "zh",
        "iw": "he",
    }
    return aliases.get(value, value)
