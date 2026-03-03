from __future__ import annotations

import argparse
import sys

from .gui import desktop_gui_available, launch_desktop_gui, show_fatal_error_dialog
from .logging_setup import (
    LOGGER,
    configure_logging,
    get_main_log_path,
    install_exception_hooks,
    write_fatal_error,
)
from .server import run_cli
from .settings import load_settings


def main() -> None:
    log_path = configure_logging()
    install_exception_hooks()
    LOGGER.info("Arranque de AlbertTranslator. log=%s", log_path)

    initial = load_settings()
    default_port = int(initial["APP_PORT"])

    parser = argparse.ArgumentParser(
        description="AlbertTranslator (GUI sin conexion o servidor CLI)"
    )
    parser.add_argument("--gui", action="store_true", help="Forzar modo GUI de escritorio")
    parser.add_argument("--cli", action="store_true", help="Ejecutar servidor en modo CLI")
    parser.add_argument(
        "--host",
        default=initial["APP_HOST"],
        help=f"Host de escucha (por defecto: {initial['APP_HOST']})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=default_port,
        help=f"Puerto de escucha (por defecto: {default_port})",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="No abrir navegador al iniciar",
    )
    args = parser.parse_args()
    LOGGER.info(
        "Argumentos recibidos: gui=%s cli=%s host=%s port=%s no_browser=%s",
        args.gui,
        args.cli,
        args.host,
        args.port,
        args.no_browser,
    )

    if args.gui and args.cli:
        parser.error("Usa --gui o --cli, no ambos.")

    cli_options_changed = (
        args.host != initial["APP_HOST"]
        or args.port != default_port
        or args.no_browser
    )

    if args.cli or (cli_options_changed and not args.gui):
        run_cli(args.host, args.port, args.no_browser)
        return

    if not desktop_gui_available():
        print("Tkinter no esta disponible. Pasando a modo CLI.")
        LOGGER.warning("Tkinter no disponible. Cambiando a modo CLI.")
        run_cli(args.host, args.port, args.no_browser)
        return

    launch_desktop_gui()


def should_show_fatal_dialog() -> bool:
    args = {arg.strip().lower() for arg in sys.argv[1:]}
    return "--cli" not in args


def run_entrypoint() -> None:
    try:
        main()
    except Exception as exc:
        try:
            configure_logging()
            LOGGER.exception("Error fatal no controlado: %s", exc)
        except Exception:
            pass

        log_path = write_fatal_error(exc)
        main_log_path = get_main_log_path()

        if should_show_fatal_dialog():
            show_fatal_error_dialog(
                "Error fatal",
                "La aplicacion se cerro por un error.\n"
                f"Revisa los logs:\n{main_log_path}\n{log_path}",
            )

        print(f"Error fatal. Revisa: {main_log_path} y {log_path}")
        raise SystemExit(1)
