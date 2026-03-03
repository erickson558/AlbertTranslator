from __future__ import annotations

import os
import logging
from typing import Dict

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from .constants import MAX_AUDIO_BYTES
from .logging_setup import LOGGER, safe_settings_for_log
from .paths import get_env_path, get_runtime_dir
from .settings import (
    coerce_chunk_ms,
    coerce_settings,
    is_valid_language_code,
    load_settings,
    normalize_transcription_backend,
)
from .speech_service import (
    detect_language_code,
    OfflineSpeechEngine,
    TranslationPairError,
    guess_extension,
    safe_delete_file,
    write_temp_audio,
)


def create_app(settings: Dict[str, str] | None = None) -> Flask:
    runtime_dir = get_runtime_dir()

    if settings is None:
        load_dotenv(get_env_path())
        settings = load_settings()
    else:
        settings = coerce_settings(settings)

    os.environ["ARGOS_CHUNK_TYPE"] = settings["ARGOS_CHUNK_TYPE"]
    LOGGER.info("Creando app Flask con settings: %s", safe_settings_for_log(settings))

    app = Flask(
        __name__,
        template_folder=str(runtime_dir / "templates"),
        static_folder=str(runtime_dir / "static"),
    )
    app.config["MAX_CONTENT_LENGTH"] = MAX_AUDIO_BYTES
    root_logger = logging.getLogger()
    app.logger.handlers = root_logger.handlers
    app.logger.setLevel(root_logger.level)
    app.logger.propagate = True

    audio_chunk_ms = coerce_chunk_ms(settings["AUDIO_CHUNK_MS"])
    engine = OfflineSpeechEngine(settings)

    @app.get("/")
    def index():
        return render_template(
            "index.html",
            audio_chunk_ms=audio_chunk_ms,
            app_host=settings["APP_HOST"],
            app_port=int(settings["APP_PORT"]),
            transcription_backend=settings["TRANSCRIPTION_BACKEND"],
        )

    @app.get("/api/health")
    def health():
        return jsonify(
            {
                "status": "ok",
                "model": engine.model_status(),
                "transcription": {"backend": engine.transcription_backend()},
                "translation": {"backend": engine.translation_backend()},
            }
        )

    @app.get("/api/model-status")
    def model_status():
        status = engine.model_status()
        status["transcription_backend"] = engine.transcription_backend()
        status["translation_backend"] = engine.translation_backend()
        return jsonify(status)

    @app.post("/api/preload-model")
    def preload_model():
        warmed = False
        try:
            warmed = engine.start_model_warmup()
        except Exception as exc:
            LOGGER.exception("Error al precargar modelo: %s", exc)
            return jsonify(
                {
                    "status": "error",
                    "state": "error",
                    "ready": False,
                    "has_local_model": False,
                    "error": str(exc),
                    "transcription_backend": engine.transcription_backend(),
                    "translation_backend": engine.translation_backend(),
                }
            ), 500

        status = engine.model_status()
        return jsonify(
            {
                "status": "ok" if warmed else "noop",
                "state": status.get("state", "ready"),
                "ready": bool(status.get("ready", True)),
                "has_local_model": bool(status.get("has_local_model", False)),
                "error": str(status.get("error", "")),
                "transcription_backend": engine.transcription_backend(),
                "translation_backend": engine.translation_backend(),
            }
        )

    @app.post("/api/transcribe-translate")
    def transcribe_translate():
        audio_file = request.files.get("audio")
        if audio_file is None:
            LOGGER.warning("Solicitud sin audio en /api/transcribe-translate.")
            return jsonify({"error": "No se recibio un bloque de audio."}), 400

        source_language = (request.form.get("source_language") or "auto").strip().lower()
        target_language = (request.form.get("target_language") or "en").strip().lower()
        language_hint = (request.form.get("language_hint") or "").strip().lower()
        requested_transcription_backend = (
            request.form.get("transcription_backend") or ""
        ).strip().lower()

        if source_language != "auto" and not source_language.isalpha():
            LOGGER.warning("Idioma origen invalido recibido: %s", source_language)
            return jsonify({"error": "Codigo de idioma origen invalido."}), 400

        if not target_language.isalpha():
            LOGGER.warning("Idioma destino invalido recibido: %s", target_language)
            return jsonify({"error": "Codigo de idioma destino invalido."}), 400
        if target_language == "auto":
            LOGGER.warning("Idioma destino 'auto' no permitido.")
            return jsonify({"error": "El idioma destino no puede ser automatico."}), 400

        transcription_backend_override = ""
        if requested_transcription_backend:
            normalized = normalize_transcription_backend(requested_transcription_backend)
            if normalized != requested_transcription_backend:
                LOGGER.warning(
                    "Backend de transcripcion invalido recibido: %s",
                    requested_transcription_backend,
                )
                return jsonify({"error": "Backend de transcripcion invalido."}), 400
            transcription_backend_override = normalized

        audio_bytes = audio_file.read()
        if not audio_bytes:
            LOGGER.warning("Se recibio bloque de audio vacio.")
            return jsonify({"error": "Se recibio un bloque de audio vacio."}), 400

        if len(audio_bytes) > MAX_AUDIO_BYTES:
            LOGGER.warning("Bloque de audio supera limite. bytes=%s", len(audio_bytes))
            return jsonify({"error": "El bloque de audio supera el limite de 25 MB."}), 400

        file_extension = guess_extension(audio_file.mimetype)
        LOGGER.info(
            "Procesando bloque de audio. bytes=%s mime=%s ext=%s source=%s target=%s hint=%s transcription_backend=%s",
            len(audio_bytes),
            audio_file.mimetype,
            file_extension,
            source_language,
            target_language,
            language_hint,
            transcription_backend_override or engine.transcription_backend(),
        )
        audio_path = write_temp_audio(audio_bytes, file_extension)

        try:
            transcript_text, detected_language = engine.transcribe_file(
                audio_path,
                source_language,
                language_hint,
                transcription_backend_override=transcription_backend_override or None,
            )
        except RuntimeError as exc:
            LOGGER.exception("Error de runtime durante transcripcion: %s", exc)
            return jsonify({"error": str(exc)}), 500
        except Exception as exc:  # pragma: no cover - runtime
            LOGGER.exception("Error inesperado durante transcripcion: %s", exc)
            return jsonify({"error": f"Fallo la transcripcion: {exc}"}), 502
        finally:
            safe_delete_file(audio_path)

        if not transcript_text:
            return jsonify(
                {
                    "transcript": "",
                    "translation": "",
                    "detected_language": detected_language,
                    "transcription_backend": transcription_backend_override
                    or engine.transcription_backend(),
                }
            )

        try:
            translated_text = engine.translate_text(
                transcript=transcript_text,
                source_language=source_language,
                detected_language=detected_language,
                target_language=target_language,
            )
        except TranslationPairError as exc:
            LOGGER.warning("Par de traduccion no disponible: %s", exc)
            return jsonify({"error": str(exc)}), 422
        except RuntimeError as exc:
            LOGGER.exception("Error de runtime durante traduccion: %s", exc)
            return jsonify({"error": str(exc)}), 500
        except Exception as exc:  # pragma: no cover - runtime
            LOGGER.exception("Error inesperado durante traduccion: %s", exc)
            return jsonify({"error": f"Fallo la traduccion: {exc}"}), 502

        return jsonify(
            {
                "transcript": transcript_text,
                "translation": translated_text,
                "detected_language": detected_language,
                "transcription_backend": transcription_backend_override
                or engine.transcription_backend(),
            }
        )

    @app.post("/api/translate-text")
    def translate_text():
        payload = request.get_json(silent=True) or {}
        transcript_text = str(payload.get("transcript", "")).strip()
        source_language = str(payload.get("source_language", "auto")).strip().lower()
        target_language = str(payload.get("target_language", "en")).strip().lower()
        detected_language = str(payload.get("detected_language", "")).strip().lower()

        if source_language != "auto" and not source_language.isalpha():
            LOGGER.warning("Idioma origen invalido en /api/translate-text: %s", source_language)
            return jsonify({"error": "Codigo de idioma origen invalido."}), 400

        if not target_language.isalpha() or target_language == "auto":
            LOGGER.warning("Idioma destino invalido en /api/translate-text: %s", target_language)
            return jsonify({"error": "Codigo de idioma destino invalido."}), 400

        if not transcript_text:
            return jsonify({"transcript": "", "translation": "", "detected_language": "auto"})

        if source_language == "auto":
            if detected_language and is_valid_language_code(detected_language):
                source_detected = detected_language
            else:
                source_detected = detect_language_code(transcript_text) or "auto"
        else:
            source_detected = source_language

        LOGGER.info(
            "Traduciendo texto directo desde frontend. chars=%s source=%s target=%s detected=%s",
            len(transcript_text),
            source_language,
            target_language,
            source_detected,
        )

        try:
            translated_text = engine.translate_text(
                transcript=transcript_text,
                source_language=source_language,
                detected_language=source_detected,
                target_language=target_language,
            )
        except TranslationPairError as exc:
            LOGGER.warning("Par de traduccion no disponible en texto directo: %s", exc)
            return jsonify({"error": str(exc)}), 422
        except RuntimeError as exc:
            LOGGER.exception("Error runtime en /api/translate-text: %s", exc)
            return jsonify({"error": str(exc)}), 500
        except Exception as exc:  # pragma: no cover - runtime
            LOGGER.exception("Error inesperado en /api/translate-text: %s", exc)
            return jsonify({"error": f"Fallo la traduccion sin conexion: {exc}"}), 502

        return jsonify(
            {
                "transcript": transcript_text,
                "translation": translated_text,
                "detected_language": source_detected,
            }
        )

    @app.post("/api/install-translation-pair")
    def install_translation_pair_api():
        LOGGER.warning("Endpoint /api/install-translation-pair deshabilitado en este build.")
        return jsonify(
            {
                "status": "disabled",
                "error": "La instalacion manual de pares esta deshabilitada en este build.",
            }
        ), 410

    return app
