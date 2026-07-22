# Spec: Boton de donacion y soporte multi-idioma en la UI web

- Estado: Implementado
- Autor: Synyster Rick (con asistencia de Claude)
- Fecha: 2026-04-23
- Version objetivo: V1.5.0 (implementado)
- Relacionado con: [`PROJECT_SPEC.md`](../PROJECT_SPEC.md) seccion 1 y 7 (i18n)

> Nota: esta spec se documenta de forma retroactiva para dejar registro del
> "por que" de una feature ya implementada, siguiendo el proceso SDD adoptado
> a partir de V1.5.1. Sirve de ejemplo de como llenar `TEMPLATE_FEATURE_SPEC.md`.

## 1. Problema / Motivacion

El proyecto es gratuito y de codigo abierto; se queria dar una via opcional y
no intrusiva para que usuarios satisfechos pudieran apoyar el mantenimiento.
Ademas, la UI web solo estaba en espanol, limitando su uso a hablantes de otros
idiomas que quisieran usar la herramienta comodamente en su propio idioma.

## 2. Objetivo

1. Agregar un boton "Comprame una cerveza" que enlace a PayPal, visible pero
   discreto (footer de la UI web).
2. Permitir cambiar el idioma de la interfaz (no el de transcripcion/traduccion,
   que ya era configurable) entre Espanol, Ingles, Portugues, Frances y Aleman,
   con la preferencia persistida entre sesiones.

## 3. No-objetivos

- No se traduce el contenido transcrito/traducido (eso ya es configurable via
  los selectores de idioma origen/destino existentes).
- No se agrega backend de pagos ni verificacion de donaciones: es un enlace
  externo simple, sin logica de servidor.

## 4. Requisitos funcionales

- [x] Boton visible en el footer con el texto "🍺 Comprame una cerveza" (o su
      traduccion segun el idioma de interfaz activo).
- [x] El boton abre `https://www.paypal.com/donate/?hosted_button_id=ZABFRXC2P3JQN`
      en una pestaña nueva (`target="_blank"`, `rel="noopener noreferrer"`).
- [x] Selector de idioma de interfaz en la esquina superior derecha del header.
- [x] Todas las cadenas visibles de la UI (titulos, botones, mensajes de error,
      estados) se traducen al cambiar el idioma de interfaz.
- [x] La preferencia de idioma de interfaz se guarda en `localStorage`
      (`albert_ui_lang`) y se restaura al recargar la pagina.

## 5. Requisitos no funcionales

- No debe requerir llamadas de red adicionales (el diccionario i18n vive en
  el propio `app.js`, no se descarga de un servidor de traducciones).
- No debe afectar el flujo de captura/transcripcion/traduccion existente.

## 6. Diseno propuesto (implementado)

- `templates/index.html`: se agrego el bloque `.donate-wrap > a#donate-btn` en
  el footer, y un `<select id="ui-language">` en un nuevo `.ui-lang-bar` en el header.
  Los elementos que muestran texto traducible obtuvieron un `id` estable para
  que `app.js` pueda actualizarlos en runtime.
- `static/app.js`: diccionario `UI_TRANSLATIONS` (uno por idioma) + funcion
  `t(key)` con fallback a espanol + `applyUiLanguage()` que actualiza el DOM +
  `wireUiLanguageSelect()` que conecta el `<select>` con `localStorage`.
- `static/style.css`: estilos `.donate-btn`, `.donate-wrap`, `.ui-lang-bar`.

## 7. Impacto en compatibilidad

Cambio puramente aditivo en la UI web; no modifica ningun contrato de API ni
el comportamiento de la GUI de escritorio o el modo CLI.

## 8. Criterios de aceptacion

- [x] El boton de donacion aparece y el enlace coincide exactamente con el
      proporcionado por el mantenedor del proyecto.
- [x] Cambiar el idioma de interfaz actualiza todos los textos visibles sin
      recargar la pagina.
- [x] Recargar la pagina conserva el ultimo idioma de interfaz elegido.

## 9. Plan de pruebas / validacion

- Prueba manual en navegador: cambiar cada idioma y verificar que titulos,
  botones, placeholders y mensajes de error cambien.
- Verificar que el enlace de donacion abre PayPal en pestaña nueva sin bloquear
  la pestaña principal de la app.

## 10. Riesgos y plan de rollback

Riesgo bajo (solo frontend). Rollback: revertir el commit que introdujo estos
cambios en `templates/index.html`, `static/app.js` y `static/style.css`.

## 11. Versionado

- Tipo de incremento aplicado: `minor` en el momento de implementacion
  original (nueva funcionalidad visible, retrocompatible) — en la practica se
  agrupo dentro del bump a V1.5.0 junto con fixes de estabilidad.
