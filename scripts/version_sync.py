#!/usr/bin/env python
"""Herramientas para mantener VERSION, README y CHANGELOG sincronizados."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path


# Rutas canonicas del proyecto. Se calculan una sola vez para no duplicar logica.
ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT / "VERSION"
README_FILE = ROOT / "README.md"
CHANGELOG_FILE = ROOT / "CHANGELOG.md"

# Formato obligatorio del versionado del proyecto.
VERSION_RE = re.compile(r"^V(\d+)\.(\d+)\.(\d+)$")
README_VERSION_RE = re.compile(r"(Version actual:\s*`)(V\d+\.\d+\.\d+)(`)")


@dataclass(frozen=True)
class AppVersion:
    """Representa una version semantica del tipo Vx.y.z."""

    major: int
    minor: int
    patch: int

    def bump(self, level: str) -> "AppVersion":
        """Devuelve la siguiente version segun el tipo de cambio solicitado."""
        if level == "major":
            return AppVersion(self.major + 1, 0, 0)
        if level == "minor":
            return AppVersion(self.major, self.minor + 1, 0)
        if level == "patch":
            return AppVersion(self.major, self.minor, self.patch + 1)
        raise ValueError("Nivel de version invalido: %s" % level)

    def __str__(self) -> str:
        return "V%d.%d.%d" % (self.major, self.minor, self.patch)


def read_text(path: Path) -> str:
    """Lee un archivo UTF-8 y falla con un mensaje claro si no existe."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit("No fue posible leer %s: %s" % (path, exc))


def write_text(path: Path, content: str) -> None:
    """Escribe archivos UTF-8 de forma consistente."""
    path.write_text(content, encoding="utf-8", newline="\n")


def parse_version(raw_value: str) -> AppVersion:
    """Convierte el texto VERSION en una estructura validada."""
    value = raw_value.strip()
    match = VERSION_RE.match(value)
    if not match:
        raise SystemExit(
            "VERSION invalida: %r. Debe tener formato Vx.x.x" % value
        )
    return AppVersion(
        int(match.group(1)),
        int(match.group(2)),
        int(match.group(3)),
    )


def read_current_version() -> AppVersion:
    """Carga y valida la version actual del proyecto."""
    return parse_version(read_text(VERSION_FILE))


def sync_readme_version(readme_text: str, version: str) -> str:
    """Actualiza la linea de version visible en README."""
    if not README_VERSION_RE.search(readme_text):
        raise SystemExit(
            "README.md no contiene una linea 'Version actual: `Vx.x.x`'."
        )
    return README_VERSION_RE.sub(r"\1%s\3" % version, readme_text, count=1)


def changelog_header(version: str) -> str:
    """Genera la cabecera base para una nueva version del changelog."""
    today = date.today().isoformat()
    return (
        "## [%s] - %s\n\n"
        "### Changed\n\n"
        "- Describe aqui los cambios principales de esta version.\n\n"
    ) % (version, today)


def ensure_changelog_entry(changelog_text: str, version: str, insert_if_missing: bool) -> str:
    """Valida o crea la entrada del changelog para la version indicada."""
    heading = "## [%s]" % version

    if heading in changelog_text:
        return changelog_text

    if not insert_if_missing:
        raise SystemExit(
            "CHANGELOG.md no contiene una entrada para %s." % version
        )

    marker = "\n## ["
    marker_index = changelog_text.find(marker)

    if marker_index == -1:
        insertion_point = len(changelog_text.rstrip()) + 1
    else:
        insertion_point = marker_index + 1

    prefix = changelog_text[:insertion_point]
    suffix = changelog_text[insertion_point:]
    block = changelog_header(version)

    if not prefix.endswith("\n\n"):
        if prefix.endswith("\n"):
            prefix += "\n"
        else:
            prefix += "\n\n"

    return prefix + block + suffix.lstrip("\n")


def command_check() -> int:
    """Verifica que VERSION, README y CHANGELOG esten alineados."""
    version = str(read_current_version())
    readme_text = read_text(README_FILE)
    changelog_text = read_text(CHANGELOG_FILE)

    if ("Version actual: `%s`" % version) not in readme_text:
        raise SystemExit(
            "README.md no esta sincronizado con VERSION. Esperado: %s" % version
        )

    ensure_changelog_entry(changelog_text, version, insert_if_missing=False)
    print("OK: version sincronizada en VERSION, README y CHANGELOG -> %s" % version)
    return 0


def command_show() -> int:
    """Imprime la version actual para scripts o validaciones manuales."""
    print(str(read_current_version()))
    return 0


def command_bump(level: str) -> int:
    """Incrementa version, sincroniza README y prepara CHANGELOG."""
    current = read_current_version()
    next_version = str(current.bump(level))

    write_text(VERSION_FILE, next_version + "\n")

    readme_text = read_text(README_FILE)
    write_text(README_FILE, sync_readme_version(readme_text, next_version))

    changelog_text = read_text(CHANGELOG_FILE)
    write_text(
        CHANGELOG_FILE,
        ensure_changelog_entry(changelog_text, next_version, insert_if_missing=True),
    )

    print(next_version)
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Define la interfaz CLI del helper de versionado."""
    parser = argparse.ArgumentParser(
        description="Sincroniza VERSION, README y CHANGELOG."
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    subcommands.add_parser("check", help="Valida que todo el versionado este alineado.")
    subcommands.add_parser("show", help="Imprime la version actual.")

    bump_parser = subcommands.add_parser(
        "bump",
        help="Incrementa la version y sincroniza documentacion.",
    )
    bump_parser.add_argument(
        "level",
        choices=("major", "minor", "patch"),
        help="Tipo de incremento semantico a aplicar.",
    )

    return parser


def main() -> int:
    """Punto de entrada del script."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "check":
        return command_check()
    if args.command == "show":
        return command_show()
    if args.command == "bump":
        return command_bump(args.level)

    parser.error("Comando no soportado.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
