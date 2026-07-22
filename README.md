# AlbertTranslator

[![Release](https://github.com/erickson558/AlbertTranslator/actions/workflows/release.yml/badge.svg)](https://github.com/erickson558/AlbertTranslator/actions/workflows/release.yml)
[![CI](https://github.com/erickson558/AlbertTranslator/actions/workflows/ci.yml/badge.svg)](https://github.com/erickson558/AlbertTranslator/actions/workflows/ci.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)

Aplicacion local para capturar audio desde el navegador, transcribirlo y traducirlo en tiempo casi real con modo web y modo escritorio.

Version actual: `V1.5.1`

## Que hace el programa

- Levanta una interfaz web local para capturar audio del microfono.
- Transcribe usando backend configurable (`google` o `faster_whisper`).
- Traduce el texto detectado usando `deep-translator` o `LibreTranslate`.
- Expone un lanzador de escritorio en Tkinter para usuarios no tecnicos.
- Genera releases automaticos en GitHub con la misma version del proyecto.

## Funcionalidades principales

- UI web local servida por Flask.
- Modo GUI con Tkinter y modo CLI para servidor local.
- Interfaz web multi-idioma (Espanol, Ingles, Portugues, Frances, Aleman), con preferencia persistida en el navegador.
- Boton de donacion "Comprame una cerveza" (PayPal) en el footer de la UI web.
- Configuracion persistente mediante `.env`.
- Health check HTTP con version visible en `/api/health`.
- Versionado centralizado con archivo `VERSION`.
- Compilacion a `.exe` con PyInstaller y icono local.
- Release automatica en GitHub con tag `Vx.x.x` por cada push valido a `main` o disparo manual del workflow.

## Requisitos

- Python 3.10 o superior.
- Windows para compilar `.exe`.
- Chrome o Edge con permiso de microfono para la experiencia web.
- Git y GitHub CLI (`gh`) para publicar cambios y releases manuales.

## Dependencias

Dependencias runtime en [requirements.txt](./requirements.txt):

- `Flask`
- `python-dotenv`
- `langdetect`
- `deep-translator`
- `SpeechRecognition`
- `faster-whisper`

Dependencias de desarrollo en [requirements-dev.txt](./requirements-dev.txt):

- runtime completo
- `pyinstaller`
- `pytest`
- `pytest-cov`
- `ruff`

## Instalacion local

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
copy .env.example .env
python app.py
```

## Uso

### Modo escritorio

```bash
python app.py
```

### Modo CLI

```bash
python app.py --cli --host 127.0.0.1 --port 8765 --no-browser
```

### Endpoints principales

- `GET /`
- `GET /api/health`
- `GET /api/model-status`
- `POST /api/preload-model`
- `POST /api/transcribe-translate`
- `POST /api/translate-text`

## Compilacion a `.exe`

El build principal se hace con [build_exe.ps1](./build_exe.ps1).

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\build_exe.ps1
```

Resultado esperado:

- `AlbertTranslator.exe` en la misma carpeta donde esta `app.py`.
- `release-artifacts\AlbertTranslator-Vx.x.x.exe`
- `release-artifacts\AlbertTranslator-Vx.x.x-win64.zip`

## Versionado

Se usa Semantic Versioning con formato obligatorio `Vx.x.x`.

- `major`: cambios incompatibles o breaking changes.
- `minor`: nuevas funciones compatibles.
- `patch`: correcciones, ajustes menores y mejoras sin romper compatibilidad.

Fuente unica de verdad:

- [VERSION](./VERSION)

Archivos sincronizados con la misma version:

- APP runtime (`/api/health` y UI)
- [VERSION](./VERSION)
- [README.md](./README.md)
- [CHANGELOG.md](./CHANGELOG.md)
- Git tag
- GitHub Release
- nombre de artefactos del release

Script recomendado para mantener todo alineado:

```bash
python scripts/version_sync.py check
python scripts/version_sync.py bump patch
python scripts/version_sync.py bump minor
python scripts/version_sync.py bump major
```

## Flujo manual recomendado para Git y GitHub

### 1. Verificar version actual

```bash
python scripts/version_sync.py check
```

### 2. Incrementar version antes del commit relevante

```bash
python scripts/version_sync.py bump patch
```

### 3. Revisar cambios

```bash
git status
git diff --stat
```

### 4. Crear commit profesional

```bash
git add .
git commit -m "feat(release): automatiza build, versionado y GitHub release Vx.x.x"
```

### 5. Subir a `main`

```bash
git push origin HEAD:main
```

### 6. Validar release publicado

```bash
gh release list --repo erickson558/AlbertTranslator --limit 5
```

## Workflow automatico de release

El workflow [release.yml](./.github/workflows/release.yml):

- se ejecuta en cada push a `main`
- valida que `VERSION`, `README` y `CHANGELOG` esten alineados
- compila el `.exe` en Windows
- crea el tag `Vx.x.x`
- publica el GitHub Release
- adjunta el `.exe` y el `.zip` de distribucion

## Estructura del proyecto

```text
.
|-- .claude/
|   |-- agents/            # Agentes de Claude Code recomendados para este repo
|   `-- skills/            # Skills de Claude Code (QA/release, GitHub, docs, SDD)
|-- .github/
|   |-- workflows/
|   |   |-- ci.yml
|   |   `-- release.yml
|-- alberttranslator/
|   |-- api.py
|   |-- constants.py
|   |-- gui.py
|   |-- main.py
|   |-- server.py
|   |-- settings.py
|   `-- speech_service.py
|-- scripts/
|   `-- version_sync.py
|-- specs/                 # Spec Driven Development: spec del proyecto + specs por feature
|-- static/
|-- templates/
|-- app.py
|-- build_exe.ps1
|-- requirements.txt
|-- requirements-dev.txt
|-- CHANGELOG.md
|-- VERSION
`-- LICENSE
```

## Desarrollo asistido con Claude Code (SDD, agentes y skills)

Este repositorio incluye herramientas de [Claude Code](https://claude.com/claude-code)
para mantener consistencia entre sesiones de desarrollo:

- **Spec Driven Development** en [`specs/`](./specs/): [`PROJECT_SPEC.md`](./specs/PROJECT_SPEC.md)
  es la especificacion viva del proyecto (arquitectura, alcance, requisitos no
  funcionales); [`specs/features/`](./specs/features/) documenta cada feature o
  fix relevante siguiendo [`TEMPLATE_FEATURE_SPEC.md`](./specs/TEMPLATE_FEATURE_SPEC.md).
- **Agentes** en [`.claude/agents/`](./.claude/agents/):
  - `qa-devops-engineer`: debugging, estabilidad, versionado SemVer y releases.
  - `code-doc-writer`: comentarios de codigo, specs SDD y documentacion (README/CHANGELOG).
- **Skills** en [`.claude/skills/`](./.claude/skills/):
  - `python-qa-release`: protocolo de analisis -> fix -> validacion -> version -> commit.
  - `github-publish`: commit/tag/push al repositorio usando la cuenta autenticada de GitHub.
  - `code-commentator`: pauta de como comentar codigo en este proyecto.
  - `spec-driven-development`: como y cuando escribir una spec antes de implementar.

## Buenas practicas operativas

- No subir `.env`, modelos locales ni logs.
- Crear una nueva version antes de cada commit relevante.
- Mantener los commits con Conventional Commits.
- No mezclar cambios funcionales y de release en un mismo commit sin necesidad.
- Probar localmente antes de empujar a `main`.

## Documentacion adicional

- [CONTRIBUTING.md](./CONTRIBUTING.md)
- [SECURITY.md](./SECURITY.md)
- [CHANGELOG.md](./CHANGELOG.md)
- [specs/PROJECT_SPEC.md](./specs/PROJECT_SPEC.md)

## Licencia

Este proyecto se distribuye bajo [Apache License 2.0](./LICENSE).
