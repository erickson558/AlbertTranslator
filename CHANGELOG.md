# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [V1.5.0] - 2026-04-23

### Added

- Boton de donacion "Comprame una cerveza" con enlace PayPal en el footer de la UI web.
- Soporte multi-idiomas en la interfaz web (ES, EN, PT, FR, DE) con selector persistente via localStorage.

### Fixed

- `is_valid_language_code()` ahora acepta codigos con guion (ej. `zh-cn`, `zh-tw`); antes `isalpha()` los rechazaba.
- `api.py`: endpoints `/api/transcribe-translate` y `/api/translate-text` usan `is_valid_language_code()` en lugar de `isalpha()` para validar codigos de idioma.
- `speech_service.py`: inicializacion de `langdetect` ahora usa `double-checked locking` para evitar condicion de carrera en entornos multi-hilo.
- `server.py`: la propiedad `running` ahora verifica tambien que el hilo del servidor este vivo, detectando cierres inesperados.
- `gui.py`: el estado de los botones del panel de escritorio se refresca automaticamente cada 2 segundos para reflejar caidas inesperadas del servidor.

## [V1.4.2] - 2026-03-28

### Changed

- Updated the release workflow so it can run on every push to `main` and also via manual `workflow_dispatch`.
- Bumped the project version to `V1.4.2` so the next release publishes with a fresh tag instead of failing on existing tag reuse.

## [V1.4.1] - 2026-03-27

### Changed

- Fixed GitHub Release asset upload so the workflow attaches the versioned `.exe` and `.zip` produced by `download-artifact`.
- Added `fail_on_unmatched_files: true` to stop the pipeline if a future release does not find its expected binaries.

## [V1.4.0] - 2026-03-27

### Changed

- Added `scripts/version_sync.py` to validate and bump `VERSION`, `README.md` and `CHANGELOG.md` together.
- Updated build strategy so the executable is produced next to `app.py` and packaged for GitHub Releases.
- Prepared release automation to compile on Windows and attach build artifacts to each push on `main`.
- Standardized development dependencies to include `pyinstaller` for reproducible builds.

## [V1.3.2] - 2026-03-12

### Changed

- Updated live translation flow in `static/app.js` to translate only the current content shown in the transcription box.
- Removed segment-by-segment translation accumulation to avoid mixed English/Spanish output.
- Added root `VERSION` file as single source of truth for app and release versioning.
- Updated `alberttranslator/constants.py` to read `APP_VERSION` from `VERSION`.
- Updated release workflow to publish GitHub Release using the exact version from `VERSION` on push to `main`.

## [V0.0.5] - 2026-03-10

### Changed

- Restored typewriter effect for live translation output in `static/app.js`.
- Added centralized app version constant and exposed version in `/api/health` and web UI.
- Synchronized version reference in README with app runtime version.

## [V0.0.1] - 2026-03-03

### Added

- Initial project structure with Flask API and Tkinter desktop launcher.
- Real-time audio transcription and translation flow.
- Configurable backends for transcription (`google`, `faster_whisper`) and translation (`google`, `libretranslate`).
- Automated GitHub Release workflow on push to `main`.
