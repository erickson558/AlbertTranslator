from __future__ import annotations

import socket


def browser_host(host: str) -> str:
    normalized = str(host or "").strip().lower()
    if normalized in {"", "0.0.0.0", "::", "*"}:
        return "127.0.0.1"
    return host


def browser_url(host: str, port: int | str) -> str:
    return f"http://{browser_host(host)}:{int(port)}"


def normalize_bind_host(host: str) -> str:
    normalized = str(host or "").strip().lower()
    if normalized in {"", "0.0.0.0", "*"}:
        return "127.0.0.1"
    if normalized == "::":
        return "::1"
    return host


def is_address_in_use_error(exc: OSError) -> bool:
    message = str(exc).lower()
    return (
        exc.errno in {98, 10048}
        or "address already in use" in message
        or "solo se permite un uso de cada direccion de socket" in message
    )


def find_available_port(host: str, start_port: int, attempts: int = 50) -> int | None:
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
    return find_available_port(host, port, attempts=1) == port
