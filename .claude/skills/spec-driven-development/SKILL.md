---
name: spec-driven-development
description: Aplica el flujo de Spec Driven Development (SDD) de AlbertTranslator antes de implementar una feature o un cambio de comportamiento no trivial. Usar cuando el usuario pida "aplicar SDD", "crear una spec", "documentar una feature antes de programarla", o cuando se vaya a construir algo nuevo (no un bugfix puntual) en este proyecto.
---

# Spec Driven Development para AlbertTranslator

Este proyecto sigue un flujo ligero de **Spec Driven Development**: antes de
escribir codigo para una feature o un cambio de comportamiento no trivial, se
deja por escrito que se quiere lograr y como se va a validar. El objetivo es
evitar sorpresas, mantener `specs/PROJECT_SPEC.md` como fuente de verdad viva,
y dejar rastro de las decisiones para quien retome el proyecto despues
(incluido un futuro agente sin memoria de esta conversacion).

## Cuando usar este flujo completo

- Nueva funcionalidad visible para el usuario (features de UI, nuevos backends,
  nuevos endpoints).
- Cambios de comportamiento o de contrato de API existentes.
- Cambios de arquitectura (nuevos modulos, cambios en como se comunican
  GUI/servidor/motor de voz).

## Cuando NO hace falta una spec nueva (pero si registrar el cambio)

- Bugfixes puntuales sin cambio de comportamiento observable: usar el flujo de
  la skill `python-qa-release` y, si el fix es significativo, documentarlo como
  una spec retroactiva corta en `specs/features/` (ver ejemplo
  `0002-fix-reinicio-servidor-tras-crash.md`).
- Cambios puramente de documentacion, comentarios o tooling interno
  (`.claude/`, `specs/`) que no afectan el comportamiento de la app.

## Flujo paso a paso

1. **Leer el contexto existente** antes de proponer nada:
   - `specs/PROJECT_SPEC.md` (vision general, arquitectura, no-objetivos).
   - `specs/features/` (features ya especificadas, para no contradecirlas).
   - El codigo relevante (los docstrings de cada modulo en `alberttranslator/`
     explican que hace cada parte).

2. **Escribir la spec** en `specs/features/NNNN-nombre-corto.md`, copiando
   `specs/TEMPLATE_FEATURE_SPEC.md` y completando cada seccion:
   - Problema/motivacion, objetivo, no-objetivos.
   - Requisitos funcionales y no funcionales, como checklist verificable.
   - Diseno propuesto: que modulos/archivos cambian, nuevos endpoints/settings.
   - Impacto en compatibilidad (¿rompe algo? ¿requiere bump `major`?).
   - Criterios de aceptacion verificables.
   - Plan de pruebas/validacion concreto (comandos, no solo "probar manualmente").
   - Tipo de incremento de version sugerido (`patch`/`minor`/`major`) y por que.

   Usar el siguiente numero correlativo (`NNNN`) segun lo que ya exista en
   `specs/features/`.

3. **Confirmar el alcance con quien pidio el cambio** si hay ambiguedad real
   (usar la herramienta de preguntas si esta disponible, o resumir la spec y
   pedir confirmacion antes de implementar cambios grandes o irreversibles).

4. **Implementar** siguiendo el diseno de la spec. Si durante la implementacion
   se descubre que el diseno no funciona, **actualizar la spec primero**, no
   solo el codigo.

5. **Validar contra los criterios de aceptacion** de la propia spec antes de
   darla por completa. Marcar los checkboxes cumplidos.

6. **Actualizar `specs/PROJECT_SPEC.md`** si el cambio afecto arquitectura,
   endpoints, configuracion o requisitos no funcionales documentados ahi.

7. **Marcar la spec como "Implementado"** en su encabezado una vez fusionada.

## Reglas importantes

- Nunca reescribir retroactivamente el "Problema/Motivacion" de una spec ya
  implementada para que encaje con lo que se termino construyendo: si el
  diseno cambio de rumbo, se documenta ese giro explicitamente.
- Las specs no sustituyen al versionado ni al commit: siguen requiriendo pasar
  por el flujo de `python-qa-release` (analisis -> fix -> validacion ->
  version -> commit -> push) para cambios que toquen codigo de la app.
- Si el cambio es puramente interno (agents/skills/specs de este mismo
  repositorio de tooling), no es necesario bump de version del `VERSION` de la
  app, pero si conviene una linea en `CHANGELOG.md` bajo "Added"/"Changed" para
  dejar rastro.
