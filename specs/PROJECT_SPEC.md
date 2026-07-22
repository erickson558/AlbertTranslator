# AlbertTranslator — Especificacion del proyecto (SDD)

> Documento vivo. Es la fuente de verdad de **que hace** AlbertTranslator y **por que**
> esta construido asi. Se actualiza junto con cada cambio funcional relevante, como
> parte del flujo de Spec Driven Development descrito en
> [`.claude/skills/spec-driven-development/SKILL.md`](../.claude/skills/spec-driven-development/SKILL.md).

- Version documentada: `V1.5.1` (debe coincidir con [`VERSION`](../VERSION))
- Ultima actualizacion: 2026-07-22

## 1. Resumen

AlbertTranslator es una aplicacion local (Windows, tambien ejecutable como script
multiplataforma) que:

1. Captura audio del microfono **desde el navegador** (no graba en el servidor).
2. Transcribe ese audio a texto, con backend configurable:
   - `google`: reconocimiento en la nube via `SpeechRecognition`/Web Speech API.
   - `faster_whisper`: modelo Whisper local (offline, sin enviar audio a terceros).
3. Traduce el texto transcrito, con backend configurable:
   - `google`: `deep-translator` (Google Translate, sin API key).
   - `libretranslate`: instancia propia o remota de LibreTranslate por HTTP.
4. Expone dos formas de uso:
   - **GUI de escritorio** (Tkinter): pensada para usuarios no tecnicos, con
     botones para configurar, arrancar/detener el servidor y abrir la web.
   - **CLI** (`--cli`): para uso avanzado/scripts, sin ventana grafica.
5. Se distribuye como un `.exe` de Windows (PyInstaller) generado por
   `build_exe.ps1`, con release automatico en GitHub via Actions.

## 2. Objetivos

- Traduccion de voz "casi en tiempo real" utilizable sin conocimientos tecnicos.
- Funcionar sin conexion cuando se elige `faster_whisper` para transcripcion
  (la traduccion en linea sigue requiriendo red salvo que se configure LibreTranslate local).
- Ser facil de compilar y distribuir como un unico `.exe` portable.
- Mantener versionado semantico estricto y consistente entre app, docs y releases.

## 3. No-objetivos (fuera de alcance actual)

- Traduccion 100% offline de texto (Argos Translate quedo como codigo legado sin
  exponer en la API; ver `alberttranslator/runtime_dependencies.py::ensure_argos_imports`).
  No se reactiva sin una decision explicita y una spec de feature dedicada.
- Soporte multiusuario/multi-sesion concurrente: el servidor corre `threaded=False`
  (una sola peticion a la vez) porque esta pensado para un unico usuario local.
- Cuentas de usuario, autenticacion o almacenamiento de historico de conversaciones.

## 4. Arquitectura

```text
app.py                          # Entry point fisico (PyInstaller apunta aqui)
alberttranslator/
  main.py            -> parsea argv, decide GUI vs CLI
  gui.py             -> panel Tkinter (config, start/stop servidor, logs)
  server.py          -> ServerController (hilo GUI) + run_cli (bloqueante)
  api.py             -> create_app(): rutas Flask + orquesta OfflineSpeechEngine
  speech_service.py  -> transcripcion (google/faster_whisper) y traduccion (google/libretranslate)
  settings.py        -> validacion/normalizacion de configuracion (.env)
  constants.py       -> defaults y VERSION (leido de /VERSION)
  network.py         -> resolucion de host/puerto, deteccion de puertos libres
  paths.py           -> rutas segun modo script vs .exe congelado
  logging_setup.py   -> logger unico + hooks de excepciones + log de fallos fatales
  runtime_dependencies.py -> imports perezosos/shims para dependencias pesadas
templates/index.html            # UI web (una sola pagina)
static/app.js                   # Logica de captura de audio, STT en vivo, i18n
static/style.css                # Estilos de la UI web
scripts/version_sync.py         # Mantiene VERSION/README/CHANGELOG sincronizados
build_exe.ps1                   # Build reproducible del .exe con PyInstaller
.github/workflows/ci.yml        # Compila y corre smoke test en cada push/PR
.github/workflows/release.yml   # Compila .exe en Windows y publica GitHub Release
```

**Flujo de datos tipico (backend `google`, navegador con Web Speech API):**

1. El navegador transcribe voz localmente (Web Speech API) -> `static/app.js`.
2. Cada resultado final se envia a `POST /api/translate-text` con el texto ya transcrito.
3. El servidor traduce y devuelve el resultado; la UI lo anima caracter a caracter.

**Flujo alternativo (backend `faster_whisper`, o navegador sin Web Speech API):**

1. El navegador graba PCM crudo con `AudioContext`/`ScriptProcessor`, lo re-muestrea
   a 16kHz y lo empaqueta como WAV.
2. Cada bloque se sube a `POST /api/transcribe-translate` (multipart/form-data).
3. El servidor transcribe con el backend activo y traduce en el mismo request.

## 5. Interfaz HTTP (API)

| Metodo | Ruta | Proposito |
| --- | --- | --- |
| GET | `/` | Sirve la UI web (`templates/index.html`). |
| GET | `/api/health` | Estado del servidor + version + backend activo. |
| GET | `/api/model-status` | Estado del modelo de transcripcion (util para Whisper). |
| POST | `/api/preload-model` | Fuerza la carga anticipada del modelo Whisper. |
| POST | `/api/transcribe-translate` | Transcribe y traduce un bloque de audio. |
| POST | `/api/translate-text` | Traduce texto ya transcrito por el navegador. |
| POST | `/api/install-translation-pair` | **Deshabilitado** (HTTP 410); legado de Argos. |

Los contratos de request/response de cada endpoint estan documentados como
docstrings en `alberttranslator/api.py`.

## 6. Configuracion

Toda la configuracion vive en `.env` (ver `.env.example`) y pasa siempre por
`settings.coerce_settings()` antes de usarse. Ver esa funcion para el listado
completo de claves y sus valores validos/por defecto.

## 7. Requisitos no funcionales

- **Estabilidad**: ninguna excepcion no controlada debe tumbar la app sin dejar
  rastro; ver `logging_setup.install_exception_hooks()` y `main.run_entrypoint()`.
- **Recuperacion ante fallos del servidor**: si el hilo del servidor muere
  inesperadamente, la GUI debe detectarlo (`ServerController.running`, polling
  cada 2s) y permitir reiniciar sin cerrar la app (`ServerController.start()`
  limpia estado obsoleto; corregido en V1.5.1).
- **Privacidad**: con backend `faster_whisper`, el audio no sale de la maquina
  para transcripcion. La traduccion en linea (`google`/`libretranslate` remoto)
  si implica enviar texto a un tercero; se documenta en README.
- **Internacionalizacion**: toda cadena de la UI web sale de
  `static/app.js::UI_TRANSLATIONS` (ES/EN/PT/FR/DE), seleccionable por el usuario
  y persistida en `localStorage`.
- **Compatibilidad**: nuevas features no deben romper los backends/endpoints
  existentes sin un cambio de version `major` y aviso explicito en CHANGELOG.

## 8. Versionado y releases

- Formato obligatorio `Vx.x.x` (Semantic Versioning), fuente unica en
  [`VERSION`](../VERSION).
- `scripts/version_sync.py` mantiene `VERSION`, `README.md` y `CHANGELOG.md`
  alineados; `ci.yml` falla el build si se desalinean.
- Cada push a `main` con una version nueva dispara `release.yml`: compila el
  `.exe` en `windows-latest`, crea el tag `Vx.x.x` y publica un GitHub Release
  con el `.exe`/`.zip` adjuntos.

## 9. Convenciones de contribucion

Ver [`CONTRIBUTING.md`](../CONTRIBUTING.md) para Conventional Commits y flujo de
rama/PR. Para features nuevas o cambios de comportamiento, seguir el proceso SDD
descrito en `.claude/skills/spec-driven-development/SKILL.md` (crear/actualizar
una spec en `specs/features/` antes de implementar).

## 10. Decisiones y deuda tecnica conocida

- `ARGOS_CHUNK_TYPE` y `ensure_argos_imports()` siguen presentes como codigo
  legado de un backend de traduccion 100% offline (Argos Translate) que ya no
  se expone en la API. No se elimina de forma preventiva para no arriesgar
  compatibilidad de configuraciones `.env` existentes; cualquier limpieza debe
  pasar por una spec dedicada.
- El servidor Werkzeug corre con `threaded=False` (una request a la vez) porque
  el caso de uso es un unico usuario local; si en el futuro se necesita atender
  varias pestanas/dispositivos a la vez, revisar la seguridad de los cachés
  compartidos (`_GOOGLE_TRANSLATOR_CACHE`, modelo Whisper) antes de habilitar
  concurrencia real.
