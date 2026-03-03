# AlbertTranslator

Aplicacion local con separacion front-end/back-end para capturar audio del microfono, transcribir y traducir en tiempo real.

## Stack actual

- Captura de audio: navegador (microfono + chunks WAV)
- Transcripcion: backend configurable (`SpeechRecognition`/Google por defecto o `faster-whisper` local opcional)
- Traduccion: backend configurable (`google` via `deep-translator` o `libretranslate` open source)
- UI web local: Flask + navegador
- Lanzador de escritorio: Tkinter

## Arquitectura

- Front-end: `templates/index.html`, `static/app.js`, `static/style.css`
- Back-end: paquete `alberttranslator/`

Modulos principales:

- `alberttranslator/api.py`: rutas Flask y contrato HTTP
- `alberttranslator/speech_service.py`: logica de traduccion/deteccion de idioma
- `alberttranslator/settings.py`: configuracion y validacion
- `alberttranslator/server.py`: arranque servidor GUI/CLI
- `alberttranslator/gui.py`: panel desktop para iniciar/detener servidor
- `alberttranslator/logging_setup.py`: logging y errores fatales

## Requisitos

- Python 3.10+
- Chrome o Edge con permiso de microfono
- Para flujo 100% local: modelo Whisper disponible en `models/whisper`
- Internet solo si eliges `TRANSCRIPTION_BACKEND=google` o `TRANSLATION_BACKEND=google`
- Traduccion:
  - `google`: requiere internet
  - `libretranslate`: puede ser local (self-hosted) o remoto

## Backend de transcripcion

Variables en `.env`:

```env
TRANSCRIPTION_BACKEND=google
WHISPER_MODEL=base
WHISPER_DEVICE=cpu
WHISPER_COMPUTE_TYPE=int8
WHISPER_LOCAL_FILES_ONLY=1
```

Valores recomendados:

- `TRANSCRIPTION_BACKEND=google` para menor latencia inicial y mejor agilidad.
- `WHISPER_LOCAL_FILES_ONLY=1` para forzar uso de modelo local.
- `TRANSCRIPTION_BACKEND=faster_whisper` para operar totalmente sin internet.
- Puedes cambiar `TRANSCRIPTION_BACKEND` desde la GUI de escritorio y desde el selector web.

## Backend de traduccion

Variables nuevas en `.env`:

```env
TRANSLATION_BACKEND=google
LIBRETRANSLATE_URL=http://127.0.0.1:5000
LIBRETRANSLATE_API_KEY=
LIBRETRANSLATE_TIMEOUT_SEC=15
```

Valores recomendados:

- `TRANSLATION_BACKEND=google` para comparar calidad tipo Google Translate.
- `TRANSLATION_BACKEND=libretranslate` para usar una opcion open source (Argos/LibreTranslate).

### Levantar LibreTranslate local (open source)

Opcion Python:

```bash
pip install libretranslate
libretranslate
```

Luego configura:

```env
TRANSLATION_BACKEND=libretranslate
LIBRETRANSLATE_URL=http://127.0.0.1:5000
```

Para Docker, revisa la guia oficial de instalacion de LibreTranslate.

## Ejecutar en desarrollo

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

## Modo CLI

```bash
python app.py --cli --host 127.0.0.1 --port 8765 --no-browser
```

## Generar .exe portable (Windows)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\build_exe.ps1
```

Salida en `dist\portable\`:

- `AlbertTranslator.exe` (o `AlbertTranslator_YYYYMMDD_HHMMSS.exe` si el nombre base esta bloqueado)
- `.env.example`
- `LEEME_PORTABLE.txt`

## Uso rapido del .exe

1. Renombra `.env.example` a `.env`
2. Ejecuta `AlbertTranslator.exe`
3. En la GUI pulsa `Guardar config` y `Iniciar servidor`
4. Abre la web y permite microfono
5. Si falla, revisa `alberttranslator.log` junto al `.exe`

## Versionado (SemVer)

El repositorio usa versionado semantico con tags `vX.Y.Z` y release automatica en cada push a `main`.

- `feat:` incrementa `MINOR` (ejemplo: `v0.1.0 -> v0.2.0`)
- `fix:` incrementa `PATCH` (ejemplo: `v0.1.0 -> v0.1.1`)
- `BREAKING CHANGE` o `!` incrementa `MAJOR` (ejemplo: `v1.2.3 -> v2.0.0`)
- Si no detecta regla, aplica `PATCH` por defecto

## Notas

- `POST /api/transcribe-translate` es el endpoint activo para audio en vivo.
- `POST /api/translate-text` traduce texto directo.
- `GET /api/health` y `GET /api/model-status` informan backend de transcripcion y traduccion activo.
- La transcripcion se procesa de forma continua mientras la escucha esta activa (sin esperar a detener).
- La interfaz web incluye botones `Copiar` para transcripcion y traduccion completas.
- `POST /api/install-translation-pair` esta deshabilitado (`410`) en este build.
- Usa la app solo con consentimiento cuando aplique legalmente.
