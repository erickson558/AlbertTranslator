---
name: python-qa-release
description: Flujo profesional de debugging, estabilidad y versionado para AlbertTranslator, actuando como ingeniero senior Python + QA + DevOps. Usar cuando el usuario pida "corregir errores", "arreglar bugs sin romper nada", "mejorar estabilidad", "preparar un commit con versionado", o describa el flujo de analisis -> correccion -> validacion -> version -> commit -> push.
---

# QA + DevOps senior para AlbertTranslator

Este skill encapsula el protocolo estricto que este proyecto espera para
cualquier ronda de correccion de errores: **analizar antes de tocar codigo**,
corregir sin romper funcionalidad, validar, versionar de forma consistente y
dejar un commit profesional listo para publicar.

## Reglas criticas (no negociables)

1. **No romper funcionalidades existentes.** El sistema ya funciona; no se
   eliminan features ni se cambia comportamiento actual salvo que sea
   exactamente el bug que se esta corrigiendo.
2. **No hacer fixes a ciegas.** Primero se analiza y se identifica la causa
   raiz; recien despues se corrige. Un fix sin entender la causa raiz es un
   riesgo, no una solucion.
3. **Consistencia de version.** Formato obligatorio `Vx.x.x`. La version debe
   coincidir siempre en: `VERSION`, `README.md` ("Version actual"), el runtime
   (`alberttranslator/constants.py::APP_VERSION`, que lee `VERSION`),
   `CHANGELOG.md`, el tag de git y el GitHub Release.
4. **No sobre-ingenieria.** Priorizar estabilidad sobre refactorizacion
   agresiva. Si hay duda sobre si algo es un bug real o solo mejorable,
   explicarlo antes de cambiarlo (ver `specs/PROJECT_SPEC.md` seccion 10 para
   deuda tecnica conocida que se deja intencionalmente).

## Fase 1 — Analisis (obligatoria, no se salta)

Antes de tocar codigo, revisar el proyecto buscando:

- Bugs funcionales y errores de logica.
- Manejo incorrecto de excepciones (bloques `except Exception` demasiado
  amplios que ocultan errores reales, o que no distinguen fallos esperables
  de inesperados).
- Problemas de concurrencia: en este proyecto, el punto critico historico es
  `alberttranslator/server.py::ServerController` (hilo del servidor vs. GUI
  Tkinter) y los locks de `alberttranslator/speech_service.py`
  (`_LANGDETECT_SEED_LOCK`, `_GOOGLE_TRANSLATOR_CACHE_LOCK`,
  `_whisper_model_lock`). Cualquier cambio ahi merece especial atencion.
- Problemas de rendimiento (recreacion innecesaria de objetos costosos: modelo
  Whisper, traductores).
- Herramientas utiles para esta fase: `python -m compileall app.py
  alberttranslator scripts`, `python -c "from alberttranslator.api import
  create_app; create_app()"`, revisar `alberttranslator.log` si existe.

Para cada hallazgo, documentar: **que es**, **causa raiz**, **impacto**,
**riesgo de la correccion**. No se corrige nada hasta tener esto claro.

## Fase 2 — Correccion

- Corregir solo lo identificado en la Fase 1.
- Mejorar manejo de errores/validaciones donde sea claramente necesario para
  el bug en cuestion (no de forma especulativa).
- Mantener el codigo comentado: si se toca una funcion sin docstring, agregar
  una breve explicacion de que hace (ver skill `code-commentator`).

## Fase 3 — Validacion

Antes de dar por buena la correccion:

- `python -m compileall app.py alberttranslator scripts` (sin errores).
- `python -c "from alberttranslator.api import create_app; create_app()"`
  (smoke test de que la app Flask sigue instanciandose).
- `python scripts/version_sync.py check` (una vez bumped la version, ver Fase 4).
- Si el bug es reproducible con un script corto, escribir una verificacion
  minima ad-hoc (en el directorio de scratch, no en el repo) que falle con el
  bug y pase con el fix, y ejecutarla.
- Confirmar que ninguna funcionalidad existente cambio de comportamiento
  fuera del bug corregido.

## Fase 4 — Versionado

Usar siempre `scripts/version_sync.py`, nunca editar `VERSION`/README a mano:

```bash
python scripts/version_sync.py check         # ver estado actual
python scripts/version_sync.py bump patch     # fix (el caso mas comun)
python scripts/version_sync.py bump minor     # nueva funcionalidad compatible
python scripts/version_sync.py bump major     # cambio incompatible
```

Esto actualiza `VERSION` y la linea "Version actual" de `README.md`, y crea un
encabezado nuevo en `CHANGELOG.md` con fecha de hoy que hay que completar con
el detalle real del cambio (reemplazar el placeholder generico).

Criterio de nivel de bump:

- `patch`: correccion de bug, mejora de estabilidad, sin cambio de contrato.
- `minor`: nueva funcionalidad visible, retrocompatible.
- `major`: cambio incompatible (rompe un endpoint, cambia un contrato, elimina
  una feature).

## Fase 5 — Commit

Mensaje estilo Conventional Commits, en el idioma que el usuario use
habitualmente en sus commits (revisar `git log` de este repo: mezcla espanol
descriptivo con prefijos en ingles), e incluir la version entre parentesis:

```text
fix: corrige reinicio del servidor tras caida inesperada del hilo (V1.5.1)
```

Antes de `git add`, correr `git status` y revisar que no se incluyan
`.env`, logs (`*.log`), `build/`, `dist/`, `release-artifacts/`, ni el
`.exe` compilado si `.gitignore` ya los excluye (deberia; no forzar su
inclusion).

## Fase 6 — Push y release

Usar la skill `github-publish` para el push/tag. Recordar que
`.github/workflows/release.yml` **ya compila el `.exe` y publica el GitHub
Release automaticamente** en cada push a `main` con una version nueva — no
hace falta compilar y publicar el release a mano salvo que se quiera verificar
el build localmente antes de subir (recomendado si el cambio toca dependencias
nativas o el propio `build_exe.ps1`).

## Entregables esperados al reportar el trabajo

1. Analisis de errores (lista, causa raiz, impacto).
2. Cambios realizados (que y como).
3. Nueva version y justificacion del nivel de bump.
4. Confirmacion de validacion (comandos corridos y resultado).
5. Mensaje de commit propuesto.
6. Comandos exactos para commit/tag/push (ver skill `github-publish`).
