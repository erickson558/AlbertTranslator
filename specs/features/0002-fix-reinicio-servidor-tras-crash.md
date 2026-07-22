# Spec: Fix — reinicio del servidor tras una caida inesperada del hilo

- Estado: Implementado
- Autor: Claude (agente `qa-devops-engineer`), a peticion de Synyster Rick
- Fecha: 2026-07-22
- Version objetivo: V1.5.1 (implementado)
- Relacionado con: [`PROJECT_SPEC.md`](../PROJECT_SPEC.md) seccion 7 (requisitos no funcionales de estabilidad)

## 1. Problema / Motivacion

En V1.5.0 se corrigio `ServerController.running` para que tambien verificara
`_thread.is_alive()` y asi detectar cuando el hilo del servidor moria de forma
inesperada (crash). Sin embargo, `ServerController.start()` seguia usando el
guard antiguo (`self._server is not None`), sin mirar si el hilo seguia vivo.

Consecuencia: si el hilo moria, la GUI detectaba correctamente `running=False`
(el polling cada 2s reactivaba el boton "Iniciar servidor"), pero al pulsarlo
`start()` lanzaba `RuntimeError("El servidor ya esta en ejecucion.")` — un
mensaje falso, ya que el servidor no estaba en ejecucion. El usuario quedaba
bloqueado sin poder reiniciar sin cerrar y reabrir toda la aplicacion.

## 2. Objetivo

Que `start()` pueda recuperarse de un hilo muerto: si detecta que el servidor
"previo" ya no tiene hilo vivo, debe limpiar ese estado obsoleto y arrancar de
nuevo con normalidad, sin exigir que el usuario reinicie la app.

## 3. No-objetivos

- No se cambia el comportamiento cuando el servidor SI esta corriendo (debe
  seguir rechazando un segundo `start()` con el mismo mensaje de error).
- No se investiga ni se corrige la causa original de un eventual crash del
  hilo (excepcion no controlada dentro de `serve_forever`); eso ya queda
  cubierto por `logging_setup.install_exception_hooks()`, que registra
  cualquier excepcion de hilo en el log.

## 4. Requisitos funcionales

- [x] `start()` usa el mismo criterio que `running` (servidor no nulo Y
      `_thread.is_alive()`) para decidir si ya hay un servidor activo.
- [x] Si `_server` no es `None` pero el hilo ya no esta vivo, se cierra el
      socket viejo (`server_close()`) y se limpia el estado antes de intentar
      un nuevo bind.
- [x] Si el servidor SI esta activo (`running=True`), `start()` sigue lanzando
      `RuntimeError("El servidor ya esta en ejecucion.")` igual que antes.

## 5. Requisitos no funcionales

- Cambio de bajo riesgo: no debe alterar el comportamiento observable en el
  camino feliz (servidor arranca y se detiene normalmente).
- Debe quedar registrado en el log (`LOGGER.warning`) cuando se limpia un
  estado obsoleto, para poder diagnosticar crashes previos revisando
  `alberttranslator.log`.

## 6. Diseno propuesto (implementado)

En `alberttranslator/server.py::ServerController.start()`:

```python
with self._lock:
    if self.running:
        raise RuntimeError("El servidor ya esta en ejecucion.")

    if self._server is not None:
        # Estado obsoleto: el hilo anterior murio inesperadamente.
        LOGGER.warning(
            "Se detecto un servidor previo con el hilo caido. "
            "Limpiando estado antes de reiniciar."
        )
        try:
            self._server.server_close()
        except Exception:
            pass
        self._server = None
        self._thread = None

    if not is_port_available(host, port):
        raise RuntimeError(...)
    ...
```

## 7. Impacto en compatibilidad

Ninguno en el camino feliz. Es un cambio puramente correctivo en una rama de
error que antes producia un mensaje enganoso.

## 8. Criterios de aceptacion

- [x] Con el servidor corriendo normalmente, un segundo `start()` sigue
      lanzando `RuntimeError("El servidor ya esta en ejecucion.")`.
- [x] Si se simula un hilo muerto (servidor detenido "a la mitad", sin pasar
      por `stop()`), `running` reporta `False` y un `start()` posterior
      arranca el servidor con normalidad, sin lanzar el error falso.
- [x] `stop()` sigue funcionando igual que antes en ambos escenarios.

## 9. Plan de pruebas / validacion

- Script de verificacion manual (`test_server_restart.py`, ejecutado durante
  el desarrollo de esta spec): arranca el controlador, fuerza el cierre del
  servidor sin pasar por `stop()` (simulando un crash del hilo), confirma
  `running=False`, y confirma que un `start()` posterior recupera el servicio
  sin lanzar `RuntimeError`.
- `python -m compileall app.py alberttranslator scripts` (sin errores de sintaxis).
- `python -c "from alberttranslator.api import create_app; create_app()"` (smoke test de import, igual que en `ci.yml`).
- `python scripts/version_sync.py check` (version/README/CHANGELOG alineados).

## 10. Riesgos y plan de rollback

Riesgo bajo. Rollback: revertir el commit que modifica `server.py` restaura el
guard anterior (`self._server is not None`), reintroduciendo el bug pero sin
afectar ninguna otra funcionalidad.

## 11. Versionado

- Tipo de incremento aplicado: `patch` (V1.5.0 -> V1.5.1). Es una correccion de
  bug sin cambios de contrato ni features nuevas para el usuario final.
