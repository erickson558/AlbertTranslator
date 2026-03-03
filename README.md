# AlbertTranslator

[![Release](https://github.com/erickson558/AlbertTranslator/actions/workflows/release.yml/badge.svg)](https://github.com/erickson558/AlbertTranslator/actions/workflows/release.yml)
[![CI](https://github.com/erickson558/AlbertTranslator/actions/workflows/ci.yml/badge.svg)](https://github.com/erickson558/AlbertTranslator/actions/workflows/ci.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)

Aplicacion local para capturar audio del microfono desde el navegador, transcribirlo y traducirlo en tiempo casi real.

## Que hace el programa

- Captura audio por bloques desde la web local (`/`).
- Transcribe usando backend configurable:
  - `google` (SpeechRecognition + servicio de Google)
  - `faster_whisper` (modelo local)
- Traduce usando backend configurable:
  - `google` (`deep-translator`)
  - `libretranslate` (self-hosted o remoto)
- Ofrece modo escritorio (GUI Tkinter) y modo servidor CLI.

## Caracteristicas principales

- Arquitectura separada `frontend` + `backend`.
- Configuracion persistente con `.env`.
- Validaciones de entrada y limites de tamano de audio (25 MB).
- Logs para diagnostico (`alberttranslator.log` y `alberttranslator_fatal.log`).
- Release automatica con tags semanticos (`vX.Y.Z`) en cada push a `main`.

## Arquitectura

- Frontend:
  - `templates/index.html`
  - `static/app.js`
  - `static/style.css`
- Backend:
  - `alberttranslator/api.py`: API Flask y rutas
  - `alberttranslator/speech_service.py`: transcripcion/traduccion
  - `alberttranslator/settings.py`: carga y validacion de configuracion
  - `alberttranslator/server.py`: arranque servidor
  - `alberttranslator/gui.py`: interfaz de escritorio
  - `alberttranslator/logging_setup.py`: logging y manejo de errores

## Requisitos

- Python 3.10 o superior
- Windows (modo GUI) o cualquier SO compatible con Flask (modo CLI)
- Chrome/Edge con permiso de microfono
- Para uso 100% local de STT: modelo Whisper en `models/whisper`
- Internet si usas `TRANSCRIPTION_BACKEND=google` o `TRANSLATION_BACKEND=google`

## Instalacion (desarrollo)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
copy .env.example .env
python app.py
```

## Uso

### Modo escritorio (default)

```bash
python app.py
```

### Modo CLI

```bash
python app.py --cli --host 127.0.0.1 --port 8765 --no-browser
```

### Build portable (.exe)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\build_exe.ps1
```

## Variables de entorno (`.env`)

| Variable | Default | Descripcion |
|---|---|---|
| `APP_HOST` | `127.0.0.1` | Host del servidor local |
| `APP_PORT` | `8765` | Puerto del servidor |
| `APP_OPEN_BROWSER` | `1` | Abre navegador al iniciar |
| `AUDIO_CHUNK_MS` | `2200` | Duracion del bloque de audio (500-30000) |
| `TRANSCRIPTION_BACKEND` | `google` | `google` o `faster_whisper` |
| `WHISPER_MODEL` | `base` | Modelo Whisper (`tiny`, `base`, `small`, `medium`, `large-v3`) |
| `WHISPER_DEVICE` | `cpu` | Dispositivo Whisper (`cpu`, `cuda`) |
| `WHISPER_COMPUTE_TYPE` | `int8` | Precision de inferencia |
| `WHISPER_LOCAL_FILES_ONLY` | `1` | Fuerza uso de modelo local |
| `TRANSLATION_BACKEND` | `google` | `google` o `libretranslate` |
| `LIBRETRANSLATE_URL` | `http://127.0.0.1:5000` | Endpoint base de LibreTranslate |
| `LIBRETRANSLATE_API_KEY` | vacio | API key opcional de LibreTranslate |
| `LIBRETRANSLATE_TIMEOUT_SEC` | `15` | Timeout de peticiones a LibreTranslate |
| `AUTO_INSTALL_TRANSLATION_PACKAGES` | `1` | Flag heredado para compatibilidad |

## API HTTP

- `GET /` interfaz web local
- `GET /api/health` estado general y backend activo
- `GET /api/model-status` estado del modelo de transcripcion
- `POST /api/preload-model` precarga modelo Whisper
- `POST /api/transcribe-translate` transcribe audio y traduce
- `POST /api/translate-text` traduce texto directo
- `POST /api/install-translation-pair` deshabilitado (`410`)

## Dependencias y buenas practicas

- `requirements.txt`: dependencias runtime con rangos compatibles (`>=`, `<`).
- `requirements-dev.txt`: herramientas de desarrollo y pruebas.
- Recomendacion para reproducibilidad fuerte:

```bash
pip install pip-tools
pip-compile requirements-dev.txt --output-file requirements-lock.txt
```

## Versionado y releases

- Se usa SemVer con tags `vX.Y.Z`.
- Workflow: `.github/workflows/release.yml`.
- Reglas por commit convencional:
  - `feat:` incrementa `MINOR`
  - `fix:` incrementa `PATCH`
  - `BREAKING CHANGE` o `!` incrementa `MAJOR`

## Flujo de colaboracion en GitHub

1. Crea una rama desde `main`.
2. Haz commits pequenos con Conventional Commits.
3. Abre Pull Request usando la plantilla.
4. Espera CI verde antes de merge.
5. Al hacer push/merge a `main`, se genera release automatica.

## Seguridad y privacidad

- No subas archivos `.env` ni tokens al repositorio.
- Usa este software solo con consentimiento de las personas grabadas.
- Revisa `SECURITY.md` para reportar vulnerabilidades.

## Documentacion adicional

- [CONTRIBUTING.md](./CONTRIBUTING.md)
- [SECURITY.md](./SECURITY.md)
- [CHANGELOG.md](./CHANGELOG.md)

## Licencia

Este proyecto se distribuye bajo licencia Apache-2.0. Ver [LICENSE](./LICENSE).
