# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

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
