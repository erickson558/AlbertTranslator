"""Utilidades de red: resolucion de host/URL para el navegador y busqueda de puertos libres."""

from __future__ import annotations

import socket


def browser_host(host: str) -> str:
    """Convierte un host de bind (p. ej. `0.0.0.0`) en uno navegable desde el navegador.

    Un servidor puede escuchar en `0.0.0.0`/`::`/`*` para aceptar conexiones en
    cualquier interfaz, pero esos valores no son URLs validas para abrir en Chrome/Edge.
    """
    normalized = str(host or "").strip().lower()
    if normalized in {"", "0.0.0.0", "::", "*"}:
        return "127.0.0.1"
    return host


def browser_url(host: str, port: int | str) -> str:
    """Construye la URL http:// completa que se abre en el navegador."""
    return f"http://{browser_host(host)}:{int(port)}"


def normalize_bind_host(host: str) -> str:
    """Normaliza un host para poder probar el bind de un socket de prueba (ver `find_available_port`)."""
    normalized = str(host or "").strip().lower()
    if normalized in {"", "0.0.0.0", "*"}:
        return "127.0.0.1"
    if normalized == "::":
        return "::1"
    return host


def is_address_in_use_error(exc: OSError) -> bool:
    """Detecta si un OSError corresponde a "puerto ya en uso" en Windows/Linux/mensajes localizados."""
    message = str(exc).lower()
    return (
        exc.errno in {98, 10048}
        or "address already in use" in message
        or "solo se permite un uso de cada direccion de socket" in message
    )


def find_available_port(host: str, start_port: int, attempts: int = 50) -> int | None:
    """Busca el primer puerto libre a partir de `start_port` intentando un bind real.

    Se usa un socket temporal por cada intento; el `with` lo cierra inmediatamente
    tras comprobar el bind, liberando el puerto para que el llamador lo use despues.
    """
    bind_host = normalize_bind_host(host)
    family = socket.AF_INET6 if ":" in bind_host else socket.AF_INET

    for port in range(start_port, min(start_port + attempts, 65536)):
        try:
            with socket.socket(family, socket.SOCK_STREAM) as test_socket:
                test_socket.bind((bind_host, port))
                return port
        except OSError:
            continue
    return None


def is_port_available(host: str, port: int) -> bool:
    """Comprueba si un puerto especifico esta libre (atajo de `find_available_port` con 1 intento)."""
    return find_available_port(host, port, attempts=1) == port
