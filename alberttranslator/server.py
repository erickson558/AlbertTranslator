"""Controlador del servidor HTTP embebido (modo GUI) y punto de entrada del modo CLI.

Este modulo expone dos formas de levantar la app Flask definida en `api.py`:
- `ServerController`: usado por la GUI de escritorio (Tkinter) para iniciar/detener
  el servidor en un hilo de fondo mientras la ventana sigue respondiendo.
- `run_cli`: usado por `main.py` cuando se ejecuta `--cli`, bloqueando el proceso
  principal en `serve_forever()`.
"""

from __future__ import annotations

import threading
from typing import Dict
import webbrowser

from werkzeug.serving import make_server

from .api import create_app
from .logging_setup import LOGGER, safe_settings_for_log
from .network import browser_url, find_available_port, is_port_available
from .settings import apply_settings_to_env, coerce_settings, load_settings, to_bool


class ServerController:
    """Arranca/detiene el servidor Werkzeug en un hilo daemon para uso desde la GUI."""

    def __init__(self) -> None:
        self._server = None
        self._thread = None
        self.url = ""
        # Serializa start()/stop() para evitar condiciones de carrera si la GUI
        # dispara ambas acciones casi al mismo tiempo (doble clic, atajos, etc.).
        self._lock = threading.Lock()

    @property
    def running(self) -> bool:
        """True solo si hay servidor Y su hilo sigue vivo.

        Comprobar unicamente `self._server is not None` no basta: si el hilo
        muere por una excepcion no controlada, `_server` seguiria sin ser None
        y la GUI creeria que el servidor sigue activo. Verificar `is_alive()`
        permite que el polling periodico de la GUI (ver gui.py) detecte
        caidas inesperadas y refresque los botones en consecuencia.
        """
        return (
            self._server is not None
            and self._thread is not None
            and self._thread.is_alive()
        )

    def start(self, settings: Dict[str, str]) -> None:
        """Crea la app Flask y la sirve en un hilo de fondo."""
        host = settings["APP_HOST"]
        port = int(settings["APP_PORT"])
        LOGGER.info("Solicitando inicio de servidor. host=%s port=%s", host, port)

        with self._lock:
            if self.running:
                raise RuntimeError("El servidor ya esta en ejecucion.")

            if self._server is not None:
                # Estado obsoleto: el hilo anterior murio inesperadamente sin pasar
                # por stop(). Si solo comparamos "_server is not None" (como antes),
                # este start() fallaria con un "ya esta en ejecucion" enganoso y el
                # usuario quedaria bloqueado sin poder reiniciar sin cerrar la app.
                # Se libera el socket viejo y se limpia el estado antes de continuar.
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
                raise RuntimeError(f"El puerto {port} no esta disponible en {host}.")

            app = create_app(settings)
            self._server = make_server(host, port, app, threaded=False)
            self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
            self._thread.start()
            self.url = browser_url(host, port)
            LOGGER.info("Servidor iniciado en %s", self.url)

    def stop(self) -> None:
        """Detiene el servidor y espera a que su hilo termine (con timeout)."""
        LOGGER.info("Solicitando detencion del servidor...")
        with self._lock:
            server = self._server
            thread = self._thread
            self._server = None
            self._thread = None
            self.url = ""

        if server is None:
            return

        server.shutdown()
        server.server_close()

        if thread and thread.is_alive():
            thread.join(timeout=2)
        LOGGER.info("Servidor detenido.")


def run_cli(host: str, port: int, no_browser: bool) -> None:
    """Levanta el servidor en el hilo principal y bloquea hasta Ctrl+C (modo `--cli`)."""
    settings = load_settings()
    settings["APP_HOST"] = host
    settings["APP_PORT"] = str(port)
    if no_browser:
        settings["APP_OPEN_BROWSER"] = "0"

    settings = coerce_settings(settings)
    apply_settings_to_env(settings)
    LOGGER.info("Iniciando modo CLI con settings: %s", safe_settings_for_log(settings))

    app = create_app(settings)
    open_browser = to_bool(settings["APP_OPEN_BROWSER"]) and not no_browser

    if open_browser:
        # Se retrasa 1s para dar tiempo a que el servidor este escuchando antes
        # de que el navegador intente conectarse.
        url = browser_url(settings["APP_HOST"], settings["APP_PORT"])
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
        LOGGER.info("Apertura automatica de navegador programada en: %s", url)

    bind_host = settings["APP_HOST"]
    bind_port = int(settings["APP_PORT"])
    LOGGER.info("Levantando servidor CLI en %s:%s", bind_host, bind_port)

    if not is_port_available(bind_host, bind_port):
        # En CLI no se reintenta automaticamente con otro puerto: se informa
        # una alternativa libre y se deja que el usuario decida.
        alternative = find_available_port(bind_host, bind_port + 1, attempts=100)
        LOGGER.error(
            "Puerto ocupado en modo CLI. host=%s port=%s alternativa=%s",
            bind_host,
            bind_port,
            alternative,
        )
        hint = f" Prueba con el puerto {alternative}." if alternative is not None else ""
        raise RuntimeError(
            f"El puerto {bind_port} no esta disponible en {bind_host}.{hint}"
        )

    try:
        server = make_server(bind_host, bind_port, app, threaded=False)
    except OSError as exc:
        LOGGER.exception("No se pudo iniciar el servidor CLI en %s:%s", bind_host, bind_port)
        raise RuntimeError(
            f"No se pudo iniciar el servidor en {bind_host}:{bind_port}: {exc}"
        ) from exc

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        LOGGER.info("Servidor CLI detenido por teclado.")
    finally:
        server.server_close()
        LOGGER.info("Servidor CLI cerrado.")
