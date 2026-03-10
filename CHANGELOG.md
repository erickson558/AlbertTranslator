# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

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
