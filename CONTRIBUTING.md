# Contributing to AlbertTranslator

Gracias por contribuir.

## Requisitos de desarrollo

- Python 3.10+
- Git

Instalacion local:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
copy .env.example .env
```

## Flujo recomendado

1. Crea una rama desde `main`.
2. Implementa cambios pequenos y atomicos.
3. Escribe commits con Conventional Commits.
4. Ejecuta validaciones locales.
5. Abre Pull Request usando la plantilla.

## Convencion de commits

- `feat:` nueva funcionalidad (sube minor)
- `fix:` correccion (sube patch)
- `docs:` solo documentacion
- `chore:` mantenimiento
- `refactor:` refactor sin cambio funcional
- `test:` pruebas
- `ci:` cambios de pipelines

Si hay cambio incompatible usa `!` o footer `BREAKING CHANGE:`.

Ejemplos:

```text
feat: agrega soporte de backend libretranslate
fix: corrige validacion de idioma destino
refactor!: cambia contrato de /api/transcribe-translate
```

## Validaciones locales

```bash
python -m compileall app.py alberttranslator
pytest -q
```

## Estilo y calidad

- Mantener funciones pequenas y legibles.
- Evitar acoplamiento entre GUI y API.
- Registrar errores con contexto suficiente en logs.
- No introducir secretos en codigo o commits.

## Pull Requests

Incluye:

- Objetivo del cambio.
- Evidencia de pruebas.
- Riesgos conocidos y plan de rollback.
- Capturas si cambia UI.
