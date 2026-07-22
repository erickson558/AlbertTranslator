---
name: code-commentator
description: Agrega comentarios y docstrings explicativos claros a codigo de AlbertTranslator para que se entienda que hace cada parte, sin caer en ruido. Usar cuando el usuario pida "comenta el codigo", "explica que hace cada parte", "necesito entender esta funcion", o antes de entregar codigo nuevo/modificado que carezca de explicacion.
---

# Comentar codigo para AlbertTranslator

El usuario de este proyecto quiere poder abrir cualquier archivo y entender
que hace cada parte sin tener que rastrear la logica linea por linea. Esta
skill prioriza claridad para un lector humano por encima de la convencion
general de "no comentar lo obvio": aqui **si** vale la pena un docstring corto
por funcion/clase, incluso cuando el nombre ya es descriptivo.

## Nivel de detalle esperado

1. **Docstring de modulo** (al tope del archivo): que hace este archivo dentro
   del proyecto y como se relaciona con los demas (quien lo importa, para que).
2. **Docstring por funcion/clase**: 1-2 lineas que digan que hace y, si no es
   obvio, por que existe o cuando se usa. No repetir el nombre de la funcion
   con otras palabras — aportar informacion nueva (el "por que", un caso de
   uso, una condicion especial).
3. **Comentarios inline** solo donde la logica no es evidente a simple vista:
   - Decisiones no obvias (p. ej. "se fuerza cpu en vez de auto por
     inestabilidad de drivers en Windows portable").
   - Invariantes o suposiciones (p. ej. "el servidor corre threaded=False,
     por eso este cache no necesita ser mas defensivo").
   - Workarounds a bugs de terceros o limitaciones conocidas.
4. **No comentar lo autoexplicativo**: una linea como `x = x + 1` o un
   `if not value: return None` no necesitan comentario si el nombre de la
   variable ya lo dice todo.

## Como trabajar

1. Leer el archivo completo antes de tocar nada — no comentar a ciegas funcion
   por funcion sin entender el flujo completo del modulo.
2. Anadir el docstring de modulo primero (da contexto para el resto).
3. Recorrer funciones/clases de arriba a abajo, anadiendo docstring donde
   falte. Si ya existe un comentario inline que cubre el "que hace", no
   duplicarlo en el docstring — consolidar en uno solo, el mas util.
4. **Nunca cambiar logica mientras se comenta.** Si al leer se detecta un bug,
   NO corregirlo en el mismo paso: anotarlo aparte y, si corresponde, invocar
   la skill `python-qa-release` para tratarlo como un cambio propio (con su
   propio analisis/version/commit).
5. Verificar que el archivo sigue compilando/importando igual que antes:
   `python -m compileall <archivo>` (Python) o revisar que no se rompio
   sintaxis JS si se edito `static/app.js`.

## Convenciones de idioma y estilo en este repo

- Los comentarios existentes en `alberttranslator/` y `static/app.js` estan en
  espanol sin tildes (para evitar problemas de encoding en logs/consolas
  Windows). Mantener esa convencion para consistencia, salvo que el usuario
  pida explicitamente lo contrario.
- Docstrings en formato simple (una o pocas lineas), no Google/NumPy style
  extenso — este proyecto no genera documentacion automatica desde docstrings,
  asi que priorizar legibilidad directa en el editor.
- No usar bloques de comentario tipo banner (`#####...#####`) salvo para
  separar secciones grandes de un archivo largo (como el resumen al tope de
  `static/app.js`), y con moderacion.

## Alcance tipico de una pasada de comentarios

Cuando se pide "comentar el proyecto" o "explicar el codigo" en general,
cubrir como minimo:

- Todos los modulos de `alberttranslator/` (`api.py`, `gui.py`, `server.py`,
  `speech_service.py`, `settings.py`, `constants.py`, `network.py`, `paths.py`,
  `logging_setup.py`, `main.py`, `runtime_dependencies.py`).
- `app.py` (entry point).
- `static/app.js` (al menos un bloque de resumen al tope, mas comentarios
  puntuales en la logica de audio/WAV/i18n que no sea evidente).
- `scripts/version_sync.py` (ya documentado; mantener ese nivel si se edita).

No hace falta comentar `templates/index.html` linea por linea; basta con
comentarios HTML puntuales donde un `id` se usa para i18n o interaccion JS no
evidente desde el propio markup (patron ya usado en ese archivo).
