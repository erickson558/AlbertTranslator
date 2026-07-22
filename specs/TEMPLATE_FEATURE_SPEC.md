# Spec: <nombre corto de la feature o cambio>

- Estado: Borrador | En implementacion | Implementado | Descartado
- Autor: <nombre>
- Fecha: <YYYY-MM-DD>
- Version objetivo: <Vx.x.x> (o "por definir" si aun no se decide el bump)
- Relacionado con: [`PROJECT_SPEC.md`](./PROJECT_SPEC.md) (seccion afectada, si aplica)

## 1. Problema / Motivacion

¿Que necesidad real motiva este cambio? ¿Que pasa hoy sin el?

## 2. Objetivo

Descripcion breve de lo que se quiere lograr, en 1-3 frases.

## 3. No-objetivos

Que queda explicitamente fuera de alcance en esta spec (para evitar scope creep).

## 4. Requisitos funcionales

- [ ] Requisito 1
- [ ] Requisito 2

## 5. Requisitos no funcionales

Rendimiento, estabilidad, privacidad, compatibilidad, i18n, etc. que apliquen.

## 6. Diseno propuesto

Como se implementa: modulos/archivos afectados, nuevos endpoints o settings,
cambios de contrato, diagramas si ayudan.

## 7. Impacto en compatibilidad

¿Rompe algo existente? ¿Requiere migrar `.env`, cambiar un contrato de API,
o es aditivo y retrocompatible?

## 8. Criterios de aceptacion

- [ ] Criterio verificable 1 (p. ej. "el boton X aparece en el footer y abre Y en pestaña nueva")
- [ ] Criterio verificable 2

## 9. Plan de pruebas / validacion

Como se va a comprobar que funciona sin romper nada existente: smoke tests,
pasos manuales, `scripts/version_sync.py check`, etc.

## 10. Riesgos y plan de rollback

Que puede salir mal y como revertir si es necesario.

## 11. Versionado

- Tipo de incremento sugerido: `patch` | `minor` | `major`
- Justificacion: <por que este nivel y no otro>
