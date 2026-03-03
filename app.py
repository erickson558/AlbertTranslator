from __future__ import annotations

from alberttranslator.api import create_app
from alberttranslator.main import main, run_entrypoint

__all__ = ["create_app", "main", "run_entrypoint"]


if __name__ == "__main__":
    run_entrypoint()
