from __future__ import annotations

from typing import Dict
import webbrowser

from .constants import (
    DEFAULT_AUDIO_CHUNK_MS,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_TRANSCRIPTION_BACKEND,
    DEFAULT_WHISPER_LOCAL_FILES_ONLY,
    DEFAULT_WHISPER_COMPUTE_TYPE,
    DEFAULT_WHISPER_DEVICE,
    DEFAULT_WHISPER_MODEL,
)
from .logging_setup import LOGGER, get_main_log_path, open_path, safe_settings_for_log
from .network import (
    browser_url,
    find_available_port,
    is_address_in_use_error,
    is_port_available,
)
from .paths import get_env_path
from .server import ServerController
from .settings import (
    apply_settings_to_env,
    coerce_settings,
    load_settings,
    save_settings,
    strict_chunk_ms,
    strict_port,
    to_bool,
)

try:
    import tkinter as tk
    from tkinter import messagebox, ttk
except Exception:  # pragma: no cover - depends on system tkinter
    tk = None
    messagebox = None
    ttk = None


def desktop_gui_available() -> bool:
    return tk is not None and ttk is not None and messagebox is not None


def show_fatal_error_dialog(title: str, message: str) -> None:
    if not desktop_gui_available():
        return

    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    except Exception:
        pass


def launch_desktop_gui() -> None:
    if not desktop_gui_available():
        raise RuntimeError("Tkinter no esta disponible en este entorno.")

    LOGGER.info("Iniciando GUI de escritorio...")
    initial = load_settings()
    controller = ServerController()

    root = tk.Tk()
    root.title("AlbertTranslator - Lanzador sin conexion")
    root.geometry("860x620")
    root.minsize(800, 560)

    def _on_tk_callback_exception(exc, value, tb) -> None:
        LOGGER.exception("Excepcion no controlada en callback Tkinter", exc_info=(exc, value, tb))
        try:
            messagebox.showerror(
                "Error en interfaz",
                "Ocurrio un error en la interfaz.\n"
                f"Revisa el log: {get_main_log_path()}",
            )
        except Exception:
            pass

    root.report_callback_exception = _on_tk_callback_exception

    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")

    whisper_model_var = tk.StringVar(value=initial["WHISPER_MODEL"])
    whisper_device_var = tk.StringVar(value=initial["WHISPER_DEVICE"])
    whisper_compute_var = tk.StringVar(value=initial["WHISPER_COMPUTE_TYPE"])
    transcription_backend_var = tk.StringVar(value=initial["TRANSCRIPTION_BACKEND"])
    whisper_local_only_var = tk.BooleanVar(value=to_bool(initial["WHISPER_LOCAL_FILES_ONLY"]))
    host_var = tk.StringVar(value=initial["APP_HOST"])
    port_var = tk.StringVar(value=initial["APP_PORT"])
    chunk_var = tk.StringVar(value=initial["AUDIO_CHUNK_MS"])
    open_browser_var = tk.BooleanVar(value=to_bool(initial["APP_OPEN_BROWSER"]))
    auto_install_var = tk.BooleanVar(
        value=to_bool(initial["AUTO_INSTALL_TRANSLATION_PACKAGES"])
    )

    pair_source_var = tk.StringVar(value="es")
    pair_target_var = tk.StringVar(value="en")

    status_var = tk.StringVar(
        value=f"Config: {get_env_path()} | Log: {get_main_log_path()}"
    )

    main = ttk.Frame(root, padding=14)
    main.pack(fill="both", expand=True)

    ttk.Label(
        main,
        text="Panel de escritorio (transcripcion navegador + traduccion)",
        font=("Segoe UI", 11, "bold"),
    ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

    ttk.Label(main, text="Modelo Whisper").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
    model_combo = ttk.Combobox(
        main,
        textvariable=whisper_model_var,
        values=["tiny", "base", "small", "medium", "large-v3"],
        state="normal",
        width=28,
    )
    model_combo.grid(row=1, column=1, sticky="ew", pady=4)

    ttk.Label(main, text="Dispositivo Whisper").grid(row=1, column=2, sticky="w", padx=(12, 8), pady=4)
    device_combo = ttk.Combobox(
        main,
        textvariable=whisper_device_var,
        values=["cpu", "cuda"],
        state="normal",
        width=28,
    )
    device_combo.grid(row=1, column=3, sticky="ew", pady=4)

    ttk.Label(main, text="Tipo de calculo").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=4)
    compute_combo = ttk.Combobox(
        main,
        textvariable=whisper_compute_var,
        values=["int8", "int8_float16", "float16", "float32", "default"],
        state="normal",
        width=28,
    )
    compute_combo.grid(row=2, column=1, sticky="ew", pady=4)

    ttk.Label(main, text="Host").grid(row=2, column=2, sticky="w", padx=(12, 8), pady=4)
    ttk.Entry(main, textvariable=host_var, width=30).grid(row=2, column=3, sticky="ew", pady=4)

    ttk.Label(main, text="Backend transcripcion").grid(
        row=3, column=0, sticky="w", padx=(0, 8), pady=4
    )
    transcription_combo = ttk.Combobox(
        main,
        textvariable=transcription_backend_var,
        values=["faster_whisper", "google"],
        state="readonly",
        width=28,
    )
    transcription_combo.grid(row=3, column=1, sticky="ew", pady=4)

    ttk.Checkbutton(
        main,
        text="Solo usar modelos Whisper locales",
        variable=whisper_local_only_var,
    ).grid(row=3, column=2, columnspan=2, sticky="w", pady=4)

    ttk.Label(main, text="Puerto").grid(row=4, column=0, sticky="w", padx=(0, 8), pady=4)
    ttk.Entry(main, textvariable=port_var, width=30).grid(row=4, column=1, sticky="ew", pady=4)

    ttk.Label(main, text="Bloque de audio (ms)").grid(row=4, column=2, sticky="w", padx=(12, 8), pady=4)
    ttk.Entry(main, textvariable=chunk_var, width=30).grid(row=4, column=3, sticky="ew", pady=4)

    ttk.Checkbutton(
        main,
        text="Abrir navegador al iniciar servidor",
        variable=open_browser_var,
    ).grid(row=5, column=0, columnspan=2, sticky="w", pady=4)

    ttk.Checkbutton(
        main,
        text="Instalar automaticamente paquetes faltantes",
        variable=auto_install_var,
    ).grid(row=5, column=2, columnspan=2, sticky="w", pady=4)

    separator = ttk.Separator(main, orient="horizontal")
    separator.grid(row=6, column=0, columnspan=4, sticky="ew", pady=(10, 10))

    ttk.Label(main, text="Instalar par de traduccion").grid(
        row=7, column=0, sticky="w", padx=(0, 8), pady=4
    )
    ttk.Label(main, text="Codigo origen").grid(row=7, column=1, sticky="w", pady=4)
    ttk.Entry(main, textvariable=pair_source_var, width=16).grid(
        row=7, column=1, sticky="e", pady=4
    )

    ttk.Label(main, text="Codigo destino").grid(row=7, column=2, sticky="w", padx=(12, 8), pady=4)
    ttk.Entry(main, textvariable=pair_target_var, width=16).grid(
        row=7, column=3, sticky="w", pady=4
    )

    info_text = (
        "Ejemplos: es->en, en->fr, de->es. "
        "Si no existe paquete directo, la app intenta pasar por en."
    )
    ttk.Label(main, text=info_text, foreground="#516173").grid(
        row=8, column=0, columnspan=4, sticky="w", pady=(0, 8)
    )

    for col in range(4):
        main.columnconfigure(col, weight=1)

    buttons = ttk.Frame(main)
    buttons.grid(row=9, column=0, columnspan=4, sticky="ew", pady=(8, 8))

    save_btn = ttk.Button(buttons, text="Guardar config")
    start_btn = ttk.Button(buttons, text="Iniciar servidor")
    stop_btn = ttk.Button(buttons, text="Detener servidor")
    open_btn = ttk.Button(buttons, text="Abrir web")
    install_btn = ttk.Button(buttons, text="Instalar par")
    logs_btn = ttk.Button(buttons, text="Abrir logs")
    exit_btn = ttk.Button(buttons, text="Salir")

    save_btn.pack(side="left", padx=(0, 8))
    start_btn.pack(side="left", padx=(0, 8))
    stop_btn.pack(side="left", padx=(0, 8))
    open_btn.pack(side="left", padx=(0, 8))
    install_btn.pack(side="left", padx=(0, 8))
    logs_btn.pack(side="left")
    exit_btn.pack(side="right")

    status_box = ttk.Label(main, textvariable=status_var, foreground="#1f2d3d")
    status_box.grid(row=10, column=0, columnspan=4, sticky="w", pady=(8, 2))

    hint_text = (
        "Permite microfono en Chrome/Edge para transcripcion en vivo. "
        "La traduccion se realiza automaticamente al recibir texto. "
        f"Si algo falla, revisa: {get_main_log_path()}"
    )
    ttk.Label(main, text=hint_text, foreground="#516173").grid(
        row=11, column=0, columnspan=4, sticky="w"
    )

    def set_button_state() -> None:
        if controller.running:
            start_btn.state(["disabled"])
            stop_btn.state(["!disabled"])
            open_btn.state(["!disabled"])
        else:
            start_btn.state(["!disabled"])
            stop_btn.state(["disabled"])
            open_btn.state(["!disabled"])

    def collect_settings() -> Dict[str, str] | None:
        requested_device = whisper_device_var.get().strip().lower()
        settings = {
            "WHISPER_MODEL": whisper_model_var.get().strip() or DEFAULT_WHISPER_MODEL,
            "WHISPER_DEVICE": requested_device or DEFAULT_WHISPER_DEVICE,
            "WHISPER_COMPUTE_TYPE": whisper_compute_var.get().strip()
            or DEFAULT_WHISPER_COMPUTE_TYPE,
            "APP_HOST": host_var.get().strip() or DEFAULT_HOST,
            "APP_PORT": port_var.get().strip() or DEFAULT_PORT,
            "APP_OPEN_BROWSER": "1" if open_browser_var.get() else "0",
            "AUDIO_CHUNK_MS": chunk_var.get().strip() or DEFAULT_AUDIO_CHUNK_MS,
            "AUTO_INSTALL_TRANSLATION_PACKAGES": "1" if auto_install_var.get() else "0",
            "TRANSCRIPTION_BACKEND": transcription_backend_var.get().strip()
            or DEFAULT_TRANSCRIPTION_BACKEND,
            "WHISPER_LOCAL_FILES_ONLY": (
                "1" if whisper_local_only_var.get() else DEFAULT_WHISPER_LOCAL_FILES_ONLY
            ),
            # Conserva configuracion de backend de traduccion para no perderla al guardar.
            "TRANSLATION_BACKEND": initial.get("TRANSLATION_BACKEND", "google"),
            "LIBRETRANSLATE_URL": initial.get("LIBRETRANSLATE_URL", "http://127.0.0.1:5000"),
            "LIBRETRANSLATE_API_KEY": initial.get("LIBRETRANSLATE_API_KEY", ""),
            "LIBRETRANSLATE_TIMEOUT_SEC": initial.get("LIBRETRANSLATE_TIMEOUT_SEC", "15"),
        }

        if not settings["APP_HOST"]:
            messagebox.showerror("Host invalido", "El host no puede estar vacio.")
            return None

        try:
            settings["APP_PORT"] = str(strict_port(settings["APP_PORT"]))
        except ValueError:
            messagebox.showerror("Puerto invalido", "El puerto debe ser un entero entre 1 y 65535.")
            return None

        try:
            settings["AUDIO_CHUNK_MS"] = str(strict_chunk_ms(settings["AUDIO_CHUNK_MS"]))
        except ValueError:
            messagebox.showerror(
                "Bloque invalido",
                "El bloque de audio debe ser un entero entre 500 y 30000 ms.",
            )
            return None

        normalized = coerce_settings(settings)
        transcription_backend_var.set(normalized["TRANSCRIPTION_BACKEND"])
        whisper_local_only_var.set(to_bool(normalized["WHISPER_LOCAL_FILES_ONLY"]))
        if requested_device == "auto" and normalized["WHISPER_DEVICE"] == "cpu":
            whisper_device_var.set("cpu")
            status_var.set(
                "WHISPER_DEVICE=auto no es estable en Windows portable. Se ajusto a cpu."
            )
            LOGGER.warning(
                "WHISPER_DEVICE=auto ajustado automaticamente a cpu para estabilidad."
            )

        return normalized

    def save_config(show_popup: bool = True) -> bool:
        settings = collect_settings()
        if settings is None:
            LOGGER.warning("No se pudo guardar configuracion: datos invalidos.")
            return False

        save_settings(settings)
        apply_settings_to_env(settings)
        LOGGER.info("Configuracion guardada: %s", safe_settings_for_log(settings))
        status_var.set(f"Configuracion guardada en {get_env_path()}")

        if show_popup:
            messagebox.showinfo("Guardado", "Configuracion guardada.")
        return True

    def start_server() -> None:
        LOGGER.info("Boton Iniciar servidor presionado.")
        if controller.running:
            status_var.set(f"El servidor ya esta ejecutandose en {controller.url}")
            LOGGER.info("Solicitud ignorada: servidor ya estaba en ejecucion (%s).", controller.url)
            return

        settings = collect_settings()
        if settings is None:
            LOGGER.warning("Inicio cancelado por configuracion invalida.")
            return

        requested_port = int(settings["APP_PORT"])
        if not is_port_available(settings["APP_HOST"], requested_port):
            free_port = find_available_port(settings["APP_HOST"], requested_port + 1, attempts=100)
            if free_port is None:
                message = (
                    f"El puerto {requested_port} no esta disponible y no se encontro otro puerto libre."
                )
                LOGGER.error(message)
                messagebox.showerror("Puerto ocupado", message)
                status_var.set(message)
                return

            LOGGER.warning(
                "Puerto %s ocupado antes de iniciar. Se cambiara automaticamente al puerto %s.",
                requested_port,
                free_port,
            )
            settings["APP_PORT"] = str(free_port)
            port_var.set(str(free_port))

        save_settings(settings)
        apply_settings_to_env(settings)

        try:
            controller.start(settings)
        except OSError as exc:
            LOGGER.exception("Error OSError al iniciar servidor: %s", exc)
            if is_address_in_use_error(exc):
                current_port = int(settings["APP_PORT"])
                free_port = find_available_port(settings["APP_HOST"], current_port + 1, attempts=100)
                if free_port is not None:
                    LOGGER.warning(
                        "Puerto %s ocupado. Reintentando inicio en puerto libre %s.",
                        current_port,
                        free_port,
                    )
                    settings["APP_PORT"] = str(free_port)
                    port_var.set(str(free_port))
                    save_settings(settings)
                    apply_settings_to_env(settings)
                    try:
                        controller.start(settings)
                    except Exception as retry_exc:
                        LOGGER.exception(
                            "Fallo el reintento de inicio con puerto %s: %s",
                            free_port,
                            retry_exc,
                        )
                        messagebox.showerror(
                            "Error al iniciar",
                            f"No se pudo iniciar el servidor: {retry_exc}",
                        )
                        status_var.set(f"Error al iniciar: {retry_exc}")
                        return

                    status_var.set(
                        f"Puerto {current_port} ocupado. Servidor ejecutandose en {controller.url}"
                    )
                    set_button_state()
                    if to_bool(settings["APP_OPEN_BROWSER"]):
                        webbrowser.open(controller.url)
                    return

            messagebox.showerror("Error al iniciar", f"No se pudo iniciar el servidor: {exc}")
            status_var.set(f"Error al iniciar: {exc}")
            return
        except RuntimeError as exc:
            LOGGER.exception("Error RuntimeError al iniciar servidor: %s", exc)
            messagebox.showerror("Error al iniciar", str(exc))
            status_var.set(str(exc))
            return

        status_var.set(f"Servidor ejecutandose en {controller.url}")
        LOGGER.info("Servidor iniciado correctamente en %s", controller.url)
        set_button_state()

        if to_bool(settings["APP_OPEN_BROWSER"]):
            webbrowser.open(controller.url)

    def stop_server() -> None:
        LOGGER.info("Boton Detener servidor presionado.")
        if not controller.running:
            status_var.set("El servidor no esta en ejecucion.")
            set_button_state()
            LOGGER.info("Detencion ignorada: servidor no estaba en ejecucion.")
            return

        controller.stop()
        status_var.set("Servidor detenido.")
        LOGGER.info("Servidor detenido desde GUI.")
        set_button_state()

    def open_web() -> None:
        LOGGER.info("Boton Abrir web presionado.")
        if controller.running:
            webbrowser.open(controller.url)
            LOGGER.info("Abriendo navegador en URL activa: %s", controller.url)
            return

        host = host_var.get().strip() or DEFAULT_HOST
        port_raw = port_var.get().strip() or DEFAULT_PORT
        try:
            port = strict_port(port_raw)
        except ValueError:
            port = int(DEFAULT_PORT)

        target_url = browser_url(host, port)
        LOGGER.info("Abriendo navegador con URL configurada: %s", target_url)
        webbrowser.open(target_url)

    def install_pair() -> None:
        LOGGER.info("Boton Instalar par presionado (funcion deshabilitada en este build).")
        status_var.set(
            "La instalacion manual de pares esta deshabilitada en este build. "
            "La traduccion se realiza en linea automaticamente."
        )
        messagebox.showinfo(
            "No disponible",
            "Esta version usa traduccion en linea y no requiere instalar pares manuales.",
        )

    def open_logs() -> None:
        log_path = get_main_log_path()
        LOGGER.info("Boton Abrir logs presionado. Archivo: %s", log_path)
        try:
            open_path(log_path)
        except OSError as exc:
            LOGGER.exception("No se pudo abrir el archivo de log: %s", exc)
            messagebox.showerror("Error al abrir logs", f"No se pudo abrir el log: {exc}")

    def close_app() -> None:
        LOGGER.info("Cierre de aplicacion solicitado desde GUI.")
        if controller.running:
            controller.stop()
        root.destroy()

    save_btn.configure(command=save_config)
    start_btn.configure(command=start_server)
    stop_btn.configure(command=stop_server)
    open_btn.configure(command=open_web)
    install_btn.configure(command=install_pair)
    logs_btn.configure(command=open_logs)
    exit_btn.configure(command=close_app)

    set_button_state()
    root.protocol("WM_DELETE_WINDOW", close_app)
    root.mainloop()
